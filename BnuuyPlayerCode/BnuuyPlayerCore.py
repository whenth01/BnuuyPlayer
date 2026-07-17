import os
import sys
import time
import shutil
import difflib
import threading
import subprocess

try:
    from . import BnuyNumUI as ui
    from . import BnuuyAudio as audio
    from . import BnuuyPlaylistManager as playlist_manager
    from . import BnuuyFileManager as file_io
    from . import BnuuyFolderManager as bnuyfolder
except(ModuleNotFoundError):
    print("BnuuyPlayer seems to be missing code, please reinstall BnuuyPlayer!")
    sys.exit()

try: 
    import requests
    import yt_dlp
except (ModuleNotFoundError, ImportError):
    print("""
A dependency failed to import or is uninstalled.

Please run) pip install yt-dlp requests""")
    sys.exit()

try:
    import mutagen
    mutagen_installed = True
except (ModuleNotFoundError, ImportError):
    print("Mutagen not installed, some features may be disabled.")
    print("To install mutagen, run) pip install mutagen")
    mutagen_installed = False

#### README ####

# Inline comments like this are treated as 'How', and 'Why'
"""Docstrings like this are treated as footnotes on what something does, not why"""
#### Comments with 4 hashes are titles. ####

############# Comments like this are important section titles #############


#### CUST EXCEPTIONS ####

"""Inner loop Escape custom function"""
# Used when escaping inner loops.
class Escape(Exception):
    pass

"""Rare Errors exception"""
# Raised as a general exception for unlikely/rare events
class RareError(Exception):
    pass

db_ref = {}

def bnuuyplayer_state(db_ref, stuff): 
    if stuff != "return pls:3":
        db_ref["bnuuydb"] = stuff
    return db_ref

#### MAIN BNUUYPLAYER CLASS ####

class BnuuyPlayer:

    def __init__(self, mutagen_installed, db_ref):

        # Assigns the if mutagen is installed bool into self
        self.mutagen_installed = mutagen_installed
        self.stop_playing_counter = False

        # General config with placeholders, overwritten once processor is done.
        self.no_hint = False
        self.initialized = False
        self.shuffl = [False, "placeholder"]
        self.ram_allocated = 10
        self.video = False
        self.time_used = 0
        self.time_playing = 0
        self.gapless_toggle = False

        # Bulk save handles saving, song paths is used in playlist picker
        self.song_paths = {}
        self.bulk_save = {}

        # Pathways for various purpose, bnuy_path is the dir BnuuyPlayer is in.
        if os.path.isdir("/storage/emulated/0/"):
            self.bnuy_path = "/storage/emulated/0/BnuuyPlayer_Database"
        else:
            self.bnuy_path = os.path.join(os.path.expanduser('~'), "BnuuyPlayer_Database")
        self.hist_path = os.path.join(self.bnuy_path, "BnuyPlayerHist.json")
        self.hist_backup1 = os.path.join(self.bnuy_path, "BnuyBackup1.json")
        self.hist_backup2 = os.path.join(self.bnuy_path, "BnuyBackup2.json")
        self.keybind_dir = os.path.join(self.bnuy_path, "bnuybinds.conf")

        """Module class init"""
        self.BnuyFolder = bnuyfolder.BnuuyFolder(self)
        self.BnuyFileManager = file_io.LoadAndRecov(self)
        self.BnuyPlaylistAdd = playlist_manager.PlaylistAdding(self)
        self.BnuyPlaylistManagement = playlist_manager.PlaylistManagement(self)
        self.BnuyDJ = audio.BnuuyDJ(self)

        """MPV Keybinds"""
        self.bnuybinds = """WHEEL_UP      add volume  2
WHEEL_DOWN    add volume -2
WHEEL_LEFT    seek -10
WHEEL_RIGHT   seek  10
+ seek  5
- seek -5
s seek  30
b seek -30
[ multiply speed 0.9
] multiply speed 1.1
{ multiply speed 0.5
} multiply speed 2.0
BS set speed 1
q quit
Q quit-watch-later
p cycle pause
SPACE cycle pause
> playlist-next
< playlist-prev
P show-progress
i script-binding stats/display-stats-toggle
G add sub-scale  0.1
F add sub-scale -0.1
9 add volume 2
0 add volume -2
m cycle mute
l cycle-values loop-file inf no"""

        """Callable dicts"""
        self.adders = {
                0: "Skip.",
                1: self.BnuyPlaylistAdd.path_adder,
                2: self.BnuyPlaylistAdd.folder_maker,
                3: self.BnuyPlaylistAdd.folder_searcher,
                4: self.BnuyPlaylistAdd.yt_adder,
                }

        # Used to filter correct and false domains
        self.valid_domains = {"youtube.com",
                "youtu.be",
                "music.youtube.com",
                "soundcloud.com",
                "bandcamp.com",
                "dai.ly",
                "vimeo.com",
                "tiktok.com",
                "vm.tiktok.com",
                "dailymotion.com",
                "old.reddit.com",
                "v.redd.it",
                "reddit.com",
                "instagr.am",
                "instagram.com",
                "fb.watch",
                "facebook.com",
                "fb.com",
                "audiomack.com",
                "mixcloud.com"}

        self.main_operations = {
               "1": ("Playlists", "Your library, your songs/playlists are here.", self.BnuyDJ.audio_funct),
               "2": ("Keybinds ","Music player keybinds.", ui.binding_menu),
               "3": ("Settings ", "Your settings, this is where important functions are.", self.settings),
               "4": ("Stats & EasterEggs", "Your statistics(such as time used)", self.stats_display),
               "5": ("Add a new Song/Playlist", "Add a Song/Playlist(online or a file system folder) here:3", self.BnuyPlaylistAdd.add_playlist),
               "e": ("Exit", "Closes BnuuyPlayer", self.exity),
                }


        """METHOD CALLS """
        self.bnuuyplayer_db_create()
        counter = threading.Thread(target=self.time_counter, daemon=True)
        counter.start()
        file_io.hist_creator(self)
        self.BnuyFolder.default_bnuuyfolders()
        self.keybind_creator()
        self.data = self.curr_bun_state("return")
        bnuuyplayer_state(db_ref, self.data)
        self.start_code()

    """BnuuyPlayer Folder dir create"""
    # This creates the folder that contains bnuuyplayer's db
    def bnuuyplayer_db_create(self):
        if not os.path.isdir(self.bnuy_path):
            try:
                os.mkdir(self.bnuy_path)
            except PermissionError:
                print("""
                      Aborting...
BnuuyPlayer has no permission to write files! 
If you are on termux,
Enter: termux-setup-storage""")
                sys.exit()

    """CTRL C exit .self backup"""

    def curr_bun_state(self, mode):
        data = self
        if mode == "return": return data

    #### BNUUYPLAYER TIME USED COUNTER ####

    """BnuuyPlayer time used"""

    def time_counter(self):
        while True:
            self.time_used += 1
            time.sleep(1)

    def time_playing_counter(self):
        while True:
            self.time_playing += 1 
            time.sleep(1)
            if self.stop_playing_counter is True: break


    #### KEYBIND CREATOR ####

    """Creates keybind .conf file"""
    # checks if keybinds dont exist
    # if they dont exist bnuybinds is written as a new file
    def keybind_creator(self):
        try:
            if not os.path.exists(self.keybind_dir):
                raise Escape

        except Escape:
            with open(self.keybind_dir, "w") as f:
                f.write(self.bnuybinds)


    #### INITIALIZER ####

    # Checks if user passed through setup, sets to True when called
    def initializer(self):
        if not self.initialized:
            self.initialized = True


    ############# XTRA METHODS #############

    def stats_display(self):
        while True:
            try:
                
                choice = ui.easter_egg_menu()
                ui.term_cleaner()

                match choice:
                    case 0: break

                    case 1: ui.time_print("using", self.time_used)

                    case 2: ui.time_print("playing music on", self.time_playing)

                    case _: raise ValueError

            except ValueError: 
                ui.term_cleaner()
                print("Invalid input!\n")
                continue



    ############# MAIN #############


    # Deprecated until further notice
    # This is being kept as it'll  be used sometime in the future, around early 2027
    # This code will likely not work in it's current form.
    # MPV Natively supports syncedLyrics, this method will just be to prettify.

    # This is due to termux MPV not supporting IPC, which this requires.
    # ToDo: Comment out all the code below.

    #class colors:
    #LIGHT_GREY = '\033[97m' # Lyrics
    #ENDC = '\033[0m' # End of print
    #BOLD = '\033[1m' # Current Lyrics

    #print(f"{colors.BOLD} text {colors.ENDC}")     # Example of how to print it


    #def lrc_funct():
    #    ui.term_cleaner()
    #    self.binding_menu()
    #    while True:
    #        if not os.path.exists(f"{bnuy_path}/.mpv_socket"):
    #            time.sleep(0.05)
    #            continue
    #        print("\n\n\n")
    #        get_time = subprocess.run("""echo '{ "command": ["get_property", "playback-time"] }' | socat - /tmp/mpvsocket""", shell=True, capture_output=True)
    #        result = get_time.stdout.decode('utf-8')
    #        print(json.loads(result))
    #        time.sleep(3)

    #### LIBRARY PRINTER ####

    def lib_print(self, local_only=False, folder_only=False, suppress_print=False):
        local_countr = 0
        stream_countr = 0 
        full_countr = 0

        local_dict = {}
        stream_dict = {}
        folder_dict = {}

        # This is meant to be overwritten by the for loop.
        # The code will use it to know if there isnt any playlists
        num = None

        full_countr = 0

        # checks if is stream is false, if it isnt then its likely online
        for num, tupl in self.song_paths.items():
            if bnuyfolder.bnuuyfolder_check(tupl):
                folder_dict[num] = self.song_paths[num]
                continue

            (name, path, is_stream, funct) = tupl

            # Begins sorting into the ints and dicts above
            if is_stream is False:
                local_countr += 1
                local_dict[num] = tupl

            else:
                stream_countr += 1 
                stream_dict[num] = tupl

            full_countr += 1

        # Combines the dicts into tmp and reenumerates the keys
        # This also has the side-effect of auto sorting stream/local.
        tmp_full_dict = local_dict | stream_dict

        # We dont neee to reenumerate here as it was already done earlier.
        full_dict = tmp_full_dict | folder_dict

        self.song_paths = full_dict

        #### DISPLAY DICT ####
        # This compiles the keys from self.song_paths into a clean architecture.
        display_keys = {}
        folder_cache = {}

        for key, tupl in self.song_paths.items():

            # I used this method to keep them temporarily separate.
            if bnuyfolder.bnuuyfolder_check(tupl): 
                folder_cache[len(folder_cache)+1] = (key, True)
            else:
                # filters out streamed entries when local_only is true
                if tupl[2] and local_only or folder_only: continue

                display_keys[len(display_keys)+1] = (key, False)

        # This ensures that folders are always after flat playlists
        folder_keys = {i: v for i, v in enumerate(folder_cache.values(), start=len(display_keys)+1)}
        display_keys = display_keys | folder_keys

        #### Playlist printer ####

        if not folder_only and not suppress_print:
            print("__________________________________________________________/\\")
            print("▼ Playlists ▼\n")

            key = None
            for key, values in display_keys.items():

                if values[1]: break # values[1] is true if the key is for a folder
                # we can break upon detection of a folder as theyre sorted and not random.
                # Although this is unnecessary, its a small performance gain

                (name, path, is_stream, funct) = self.song_paths[values[0]]

                if is_stream is True and not local_only:
                    print(f"{key}) {name} (Online stream.)")

                elif is_stream is False:
                    print(f"{key}) {name}")

            if len(local_dict) == 0 and len(stream_dict) == 0:
                print("No playlists.")

        #### Folder printer ####
        if not suppress_print:
            print("__________________________________________________________\\/")
            print("▼ BnuuyFolders ▼                                          /\\\n")

            printed = False
            for disp_num, (og_key, is_folder) in display_keys.items():
                tupl = self.song_paths[og_key]

                if is_folder:
                    printed = True
                    print(f"{disp_num}) {tupl[1]} ({tupl[0]})")

            if not printed:
                print("No folders found.")

        print_results = {
            "full_dict": full_dict,
            "stream_dict": stream_dict,
            "local_dict": local_dict,
            "folder_dict": folder_dict,

            "display_keys": display_keys,
            "folder_keys": folder_cache,

            "full_countr": full_countr,
            "stream_countr": stream_countr,
            "local_countr": local_countr,
            }

        return print_results

    #### FILE.MOVER ####
    def move_file(self, path):
        while True:
            try:
                res = self.lib_print(local_only=True)

                library = res.get("full_dict")
                display_keys = res.get("display_keys")

                selection = ui.move_file_menu()

                if selection == 0: break 

                if bnuyfolder.bnuuyfolder_check(library[display_keys[selection][0]]):
                    raise ValueError

                _, dest_path, is_stream, _ = library[display_keys[selection][0]]

                if is_stream:
                    ui.general_exception("Wrong number entered!")
                    continue

                confirm = ui.confirm(path, dest_path)
                if confirm == 1:
                    lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
                    lrc_path = os.path.join(os.path.dirname(path), lrc_file)
                    if os.path.isfile(lrc_path):
                        try:
                            shutil.move(lrc_path, dest_path)
                        except shutil.Error:
                            ui.general_exception("Lyric file already exists in that directory:( skipping..")
                            continue
                    try:
                        shutil.move(path, dest_path)
                    except shutil.Error:
                        ui.general_exception("File already exists in that directory :( Canceling..")
                        continue

                    print("Successfully moved file!")

                elif confirm == 0: break 

                else: raise ValueError

            except (ValueError, KeyError):
                ui.general_exception()
                continue

    #### CMD HANDLER ####

    def cmd_handler(self, params):
        cmd = params.get("cmd")
        path = params.get("path")

        if os.path.isdir(path):
            print("Selected song turned out to be a Folder, cancelling..")
            return

        match cmd:

            case "l":
                """Like a song"""
                success = False
                for _, tupl in self.song_paths.items():
                    if bnuyfolder.bnuuyfolder_check(tupl) and tupl[0] == "liked_songs":
                        if path in tupl: 
                            ui.special_exception("Song already liked! aborting..")
                            return
                        tupl.append(path)
                        self.BnuyFileManager.saver()
                        print("Successfully liked song!")
                        success = True
                        break

                    else: success = False

                if success is False:
                    print("Song not found! :( aborting..")
                    return
            case "d":
                """Delete song"""
                check = os.path.isfile(path)

                if check is False: 
                    print("Cannot delete streamed songs from disk or folders from this menu.")
                    return
                else:
                    while True:
                        confirm = ui.cmd_handler_del_confirm(path)

                        if confirm == "1": break 

                        elif confirm == "0": return 

                        else:
                            ui.general_exception("Enter 1 or 0")
                            continue

                    os.remove(path)
                    # This deletes the .lrc file.
                    lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
                    for root, dirs, files in os.walk(os.path.dirname(path)):
                        if lrc_file in files:
                            os.remove(os.path.join(root, lrc_file))
                            print(f"Successfully deleted) {lrc_file}")
                            break

                    print(f"Successfully deleted) {os.path.basename(path)}")

            case "m":
                """Move song"""
                self.move_file(path)

            case "c":
                """Copy song"""
                while True:
                    try:

                        res = self.lib_print()
                        select = ui.cmd_handler_copy_confirm(path)

                        if select == 0:
                            ui.term_cleaner()
                            print("Cancelling...")
                            return

                        else:
                            keys = res.get("display_keys")
                            library = res.get("full_dict")
                            selected = library.get(keys.get(select)[0])
                            err = False

                            if selected is None:
                                """No match check"""
                                err = True
                                message = "Invalid input, no matching entry."

                            elif bnuyfolder.bnuuyfolder_check(selected):
                                """Folder check"""
                                err = True
                                message = "Invalid input, select a playlist and not a folder."

                            elif selected[2]:
                                """Streamed entry check"""
                                err = True
                                message = "Cannot copy to streamed entries!"

                            else: 
                                _, dest_path, is_stream, _ = selected

                            if err:
                                ui.special_exception(message)
                                continue

                            # This attempts to copy the .lrc file into the dest.
                            lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
                            lrc_path = os.path.join(os.path.dirname(path), lrc_file)
                            if os.path.isfile(lrc_path):
                                try: shutil.copy(lrc_path, dest_path)

                                except shutil.SameFileError: pass

                            # Copies the selected file aswell.
                            try: 

                                shutil.copy(path, dest_path)
                                ui.term_cleaner()
                                print("Successfully copied file!")
                                continue

                            except shutil.SameFileError:
                                ui.special_exception("File already exists in the destination!")
                                continue

                    except ValueError:
                        ui.general_exception()
                        continue

                    except TypeError:
                        ui.special_exception("Invalid number.")
                        continue

            case "p":
                """Play song"""
                return path

            case _:
                ui.general_exception()
                return

    #### SEARCH LIBRARY ####

    def investibun_search(self):
        invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".wma", ".lrc", ".py"}
        lib_dict = self.lib_print(local_only=False, folder_only=False, suppress_print=True)
        keys = lib_dict.get("display_keys")
        lib_dict = {}
        while True:
            try:

                search_select = ui.investibun_main()

                if search_select == "0":
                    return

                search_query = ui.investibun_query()
                
                if search_query == "0":
                    return

                entries = {}
                songs = []
                playlists = []
                song_handler = False
                playlist_handler = False

                for key, tupl in self.song_paths.items():
                    if bnuyfolder.bnuuyfolder_check(tupl) is True: continue

                    else: name, path, is_stream, _ = tupl

                    if search_select == "2": 
                        """Playlist route"""
                        disp_name = name
                        duplicates = 1

                        entries[len(entries)+1] = path, is_stream, name.lower(), key, disp_name
                        playlists.append(name.lower())
                        playlist_handler = True

                    elif search_select == "1":
                        """Songs route"""
                        if os.path.isdir(path):

                            compiler = []
                            for name in os.listdir(path):
                                split = os.path.splitext(name)
                                if split[1] in invalid_ext: continue
                                compiler.append(split[0].lower())

                            entries[key] = compiler
                            songs += compiler
                            song_handler = True

                        else: continue

                    else:
                        ui.general_exception()
                        break

                else:

                    if song_handler:
                        search = set(difflib.get_close_matches(search_query.lower(), songs, n=3, cutoff=0.5))
                    else:
                        search = set(difflib.get_close_matches(search_query.lower(), playlists, n=3, cutoff=0.5))
                    
                    info = {
                        "search": search,
                        "entries": entries,
                        "playlists": self.song_paths,
                        "playlist_handler": playlist_handler,
                    }

                    ui.basic_result_print(info)

            except ValueError:
                ui.general_exception()
                continue

    #### METADATA COMPILER & BACKEND ####

    def bulk_helper(self, params, mode, dest_path):

        processed_files = 0

        for num, (metadata, path, key) in params.items():
            if not os.path.isdir(dest_path):
                ui.special_exception("Destination path was deleted, please select a new playlist!")
                break

            # This is a blacklist of files to prevent copy from overwriting same name files
            if mode == "copy": files = set(os.listdir(dest_path))
            # moving doesnt need it as it raises an error
            else: files = {}

            lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
            lrc_path = os.path.join(os.path.dirname(path), lrc_file)

            moved_song = False
            if not os.path.isfile(path):
                print(f"{os.path.basename(path)} is missing or deleted, skipping..")
                continue

            try:
                handled = False
                if mode == "move":
                    shutil.move(path, dest_path)
                    handled = True
                    msg = f"{os.path.basename(path)} was moved to {os.path.basename(dest_path)}"

                elif mode == "copy" and os.path.basename(path) not in files:
                    shutil.copy(path, dest_path)
                    handled = True
                    msg = f"{os.path.basename(path)} was copied to {os.path.basename(dest_path)}"


                elif mode == "delete":
                    os.remove(path)
                    handled = True
                    msg = f"{os.path.basename(path)} was deleted."

                
                elif mode == "play":
                    player = [
                        "mpv",
                        path,
                        f"--input-conf={self.keybind_dir}",
                        "--profile=fast",
                        "--no-video"
                        ]
                    try:
                        subprocess.run(player, check=True)
                        continue
                    except subprocess.CalledProcessError as e:
                        print(f"An error occurred!")
                        print(e)

                if handled:
                    print(msg)
                    processed_files += 1
                    moved_song = True
                else:
                    print(f"{os.path.basename(path)} failed to be copied due to another file with the same filename existing in the chosen playlist!")
                    moved_song = False
                    processed_files += 1 

            except(shutil.Error, PermissionError, FileNotFoundError, OSError) as e:
                print("An error occurred while handling the song file!")
                print(e)
                print("Skipping song..")
                continue
            
            if os.path.isfile(lrc_path) and moved_song:
                try:
                    handled = False

                    if mode == "move":
                        shutil.move(lrc_path, dest_path)
                        msg = f"{lrc_file} was moved to {os.path.basename(dest_path)}"
                        handled = True

                    elif mode == "copy" and lrc_file not in files:
                        shutil.copy(lrc_path, dest_path)
                        msg = f"{lrc_file} was copied to {os.path.basename(dest_path)}"
                        handled = True

                    elif mode == "delete":
                        os.remove(lrc_path)
                        msg = f"{lrc_file} was deleted."
                        handled = True

                    if handled:
                        print(msg)
                        processed_files += 1
                    else:
                        # only copy route failing doesnt raise an exception
                        print(f"{lrc_file} failed to be copied due to another file with the same filename existing in the chosen playlist!")
                        processed_files += 1

                except(shutil.Error, PermissionError, FileNotFoundError, OSError) as e:
                    print("An error occurred while handling the lyric file!")
                    print(e)
                    print("Skipping lyric file..")
                    continue

        print("Finished handling the files!:3")
        return processed_files


    #### MULTIPLE FILE MOVER ####
    # Note: all of these are currently unfinished
    def bulk_mover(self, params):
        while True:
            try:
                res = self.lib_print(local_only=True)
                selection = ui.bulk_move_select()

                if selection == 0:
                    return
                
                keys = res.get("display_keys")
                selected_playlist = self.song_paths[keys[selection][0]]

                # is folder check
                if keys[selection][1]:
                    print("Can not select a folder, please select a playlist.")
                    continue
                # Stream check
                elif selected_playlist[2]: raise ValueError

                dest_path = selected_playlist[1]

                while True:
                    confirm = ui.bulk_move_confirm(params, selected_playlist[0])

                    if confirm == "0": break
                    
                    elif confirm == "1":
                        amount_moved = self.bulk_helper(params, "move", dest_path)

                        print(f"Moved {amount_moved} files!:3")
                        return

                    else:
                        ui.general_exception()
                        continue

            except (ValueError, KeyError):
                ui.special_exception("Please select a playlist, not a folder or streamed entry.")
                continue


    #### MULTIPLE FILE COPY ####

    def bulk_copy(self, params):
        copy_size_bytes = 0 
        for _, (_, path, _,) in params.items():
            if os.path.isfile(path):
                copy_size_bytes += os.path.getsize(path)

        copy_size_kb = copy_size_bytes / 1024
        copy_size_mb = copy_size_kb / 1024
        copy_size_gb = copy_size_mb / 1024

        while True:
            try:
                res = self.lib_print(local_only=True)

                dest_select = ui.bulk_copy_dest_menu()

                if dest_select == 0:
                    return

                keys = res.get("display_keys")

                selected_playlist = self.song_paths[keys[dest_select][0]]
                # folder check
                # keys hold a is folder value at index 1
                if keys[dest_select][1]:
                    ui.special_exception("Cannot select a folder :(, please select a playlist!")
                    continue

                # stream check
                elif selected_playlist[2]: raise ValueError

                confirm_loop = True
                while confirm_loop:
                    info = {
                        "playlist": self.song_paths[keys[dest_select][0]][0],
                        "params": params,
                        "mb": copy_size_mb,
                        "gb": copy_size_gb,
                    }

                    confirm = ui.bulk_copy_confirm(info)

                    if confirm == "1": pass

                    elif confirm == "0":
                        confirm_loop = False
                        break

                    else:
                        print("Invalid input, pick 1 or 0.")
                        continue

                
                    name, dest_path, _, _, = selected_playlist

                    amount_copied = self.bulk_helper(params, "copy", dest_path)

                    print(f"Copied {amount_copied} files!:3")
                    return


            except (ValueError, KeyError):
                ui.general_exception("Please select a playlist")
                continue

    #### METADATA BASED BULK DELETE ####

    def bulk_delete(self, params):
        while True:
            try:
                confirm = ui.bulk_del_confirm(params)


                if confirm == 1:
                    # spoofing the dest path to make it fit in
                    amount_deleted = self.bulk_helper(params, "delete", self.bnuy_path)
                    print(f"Deleted {amount_deleted} files.")
                    return 

                elif confirm == 0:
                    return

                else: raise ValueError

            except ValueError:
                ui.general_exception("Select 0 or 1.")
                continue

    #### METADATA BASED PLAYBACK ####

    def metadata_player(self, params):
        self.bulk_helper(params, "play", self.bnuy_path)

    #### Mutagen advanced search ####

    def advanced_investibunny(self):
        if self.mutagen_installed is False:
            print("Mutagen is uninstalled. to access this run) pip install mutagen")
            return

        bulk_methods = {
        "1": self.bulk_mover,
        "2": self.bulk_copy,
        "3": self.bulk_delete,
        "4": self.metadata_player
        }

        # Generally unsupported extensions
        invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".wma", ".lrc", ".py"}
        # Extensions that are unsupported by Mutagen
        unsupported_ext = {".webm", ".mkv", ".it", ".avi", ".mov", ".mpg", ".mpeg", ".ts", ".flv", ".3gp"}
        # valid search tags
        tags = {
            "artist": "artist",
            "title": "title",
            "album": "album",
            "genre": "genre",
            }
        # every menu below this hasnt been pushed to BnuyNumUI.py
        while True:
            try:


                selection = ui.advanced_select_query()

                values = selection.split()
                if values[0] == "0": return

                elif len(values) < 2: raise ValueError

                else:
                    tag = tags.get(values[0])

                    if tag is None: raise ValueError

                    # reconstructs the string 
                    # 0 is the tag (as seen above)
                    query = " ".join(values[1:])
                    results = {}
                    # this starts by searching playlists in self.song_paths 
                    # for their metadata
                    for num, tupl in self.song_paths.items():
                        if bnuyfolder.bnuuyfolder_check(tupl): continue
                        
                        name, path, is_stream, _ = tupl
                        
                        if not is_stream:
                            # then begins looking through local songs..
                            if not os.path.isdir(path):
                                print(f"Encountered an invalid playlist) {name}\nIgnoring...")
                                continue
                            for file in os.listdir(path):
                                # filters invalid songs and files
                                if os.path.splitext(file)[1].lower() in invalid_ext: 
                                    continue
                                full_file = os.path.join(path, file)
                                # collects the metadata
                                try:
                                    metadata = mutagen.File(full_file, easy=True)
                                except mutagen.MutagenError as e:
                                    print("An error occurred! ▼")
                                    print(e)
                                    print("Ignoring the file..")
                                    continue

                                if os.path.splitext(file)[1] in unsupported_ext:
                                    print(f"{file} is unsupported.")
                                    continue

                                elif metadata is None or len(metadata) == 0:
                                    print(f"{file} had no metadata.")
                                    continue

                                # pulls the selected tag from the metadara
                                value = metadata.get(tag)

                                if value is None:
                                    print(f"{file} did not have {tag} in its metadata :(")
                                    continue

                                for data in value:
                                    # fuzzy search through the results
                                    check = difflib.SequenceMatcher(None, data.lower(), query.lower()).ratio()
                                    if check < 0.5: 
                                          print(f"{file} did not match.")
                                          continue
                                    # if its a match > 0.3, it saves the result
                                    else: 
                                        results[len(results)+1] = (metadata, full_file, num)
                                        break

                    while True:

                        if len(results) == 0:
                            print("\nNo results found:(")
                            break

                        else:
                            ui.advanced_result_print(results, self.song_paths)
                            choice = ui.advanced_result_selection()

                            funct = bulk_methods.get(choice)
                            if choice == "0": break

                            elif funct is None: 
                                ui.general_exception("Select a number between 0-4")
                                continue

                            else: 
                                ui.term_cleaner()
                                funct(results)
                                break

            except ValueError:
                ui.general_exception("Read BnuuyPlayer's README.md help section.")
                continue

            except IndexError:
                ui.general_exception()
                continue

    #### LYRIC DOWNLOAD ####

    def lrc_dl(self):

        while True:
            confirm = ui.lrc_dl_confirm()

            if confirm == "1": break
            elif confirm == "0": return
            else:
                ui.general_exception("Select 1 or 0.")
                continue

        # Downloads lyrics for existing songs
        for _, tupl in self.song_paths.items():
            # folder check
            if bnuyfolder.bnuuyfolder_check(tupl): continue
            # is stream check
            if tupl[2]: continue

            name, path, _, _, = tupl

            print(f"Beginning download for {os.path.basename(path)}")

            d = {"status": "finished", 
                 "filename": "placeholder",
                 "filepath": path,
                 "info_dict": {},}
            try:
                files = os.listdir(path)
            except FileNotFoundError:
                ui.special_exception("The playlist's folder was deleted or is missing, aborting!")
                print(f"Missing the folder) {os.path.basename(path)}")
            for file in os.listdir(path):

                if os.path.isdir(os.path.join(path, file)): continue

                try:
                    metadata = mutagen.File(os.path.join(path, file), easy=True)
                except mutagen.MutagenError as e:
                    print(f"An unknown error occurred!) {e}")
                    continue

                if metadata is None:
                    print(f"{file} is unsupported, or had no metadata! skipping..")
                    continue

                artist = metadata.get("artist")
                title = metadata.get("title")
                album = metadata.get("album")
                fallback = False

                err = False
                if artist is None or title is None or album is None: err = True

                elif len(artist) == 0 or len(album) == 0: err = True

                if err:
                    print(f"{file} had missing metadata, cannot download!")
                    continue 
                if len(title) == 0:
                    print("No title metadata :(, fallbacking to filename.")
                    title = os.path.splitext(file)[0]
                    fallback = True


                artist = artist[0]
                if fallback: pass
                else: title = title[0]
                album = album[0]

                duration = metadata.info.length
                # spoofs the info dict for yt dlp hook
                d["info_dict"] = {"artist": artist, 
                                  "title": title,
                                  "album": album,
                                  "duration": duration,}
                d["filename"] = os.path.join(path, file)

                self.yt_hook(d)


    ############# MAIN FOLDER/SETUP AREA #############

    #### EXIT FUNCT ####

    def exity(self):
        sys.exit()

    #### YT-dlp Hook ####

    """LRC downloader"""

    # d contains information from yt-dlp, which my code then gets the information
    # needed for a lrclib API lookup for lyrics.
    # Additional note; plainLyrics are currently unsupported by MPV, but V6 will
    # fix that via IPC
    def yt_hook(self, d):
        if d["status"] == "finished":

            info_dict = d["info_dict"]

            title = info_dict.get("title")
            artist = info_dict.get("artist")
            duration = info_dict.get("duration")
            album = info_dict.get("album")

            if artist is None: artist = info_dict.get("uploader")


            try:
                """lrclib lookup"""
                lrc_get = requests.get(f"https://lrclib.net/api/get?artist_name={artist}&track_name={title}&album_name={album}&duration={duration}", timeout=10)

            except(requests.exceptions.Timeout):
                print("\nTimeout!")
                return

            except(requests.exceptions.ConnectionError):
                print("\nInternet connection dropped, unable to download!")
                return

            
            # if lrclib responds successfully, attempt to find lyrics
            if lrc_get.status_code == 200:
                data = lrc_get.json()

                lyricsync = data.get('syncedLyrics')
                lyricplain = data.get('plainLyrics')

                print("\n\nAttempting to fetch lyrics..")


                # Attempt to find lrc format, if none are found inform and quit
                if lyricsync is not None:
                    lyric = lyricsync
                    print("\nSynced lyrics autoselected.")
                elif lyricplain is not None:
                    print("\nNo synced lyrics available, defaulting to plain.")
                    lyric = lyricplain
                else:
                    print("\nNo lyrics found!")
                    return

                # extracts basename, then uses splitext to split into [name, ext]
                # and uses [0] to select the name
                base_name = os.path.splitext(os.path.basename(d["filename"]))[0]

                # combines the processed dir with processed basename and .lrc
                lrc_path = os.path.join(os.path.dirname(d["filename"]), f"{base_name}.lrc")

                try:
                    with open(lrc_path, "w") as f:
                        f.write(lyric)
                except OSError as e:
                    print(f"\nEncountered a OS Error when writing the .lrc! ▼\n\n{e}")
                    return

                except PermissionError:
                    print("BnuuyPlayer has no permission to write files.")
                    return

                # 404 means no lyrics found as per lrclib responses

            elif lrc_get.status_code == 404:
                print("\n No lyrics found!")

            else:
                print(f"\nUnknown error) {lrc_get.status_code} \n Lyrics not saved.")

    #### SITE WHITELIST HANDLER ####

    def site_whitelist_handler(self):
        while True:
            try:

                site_amount, domains = ui.site_printer(self.valid_domains)

                select = ui.whitelist_site_main()

                if select == 0: return
                
                elif select == 1:
                    add_site = ui.enter_new_site()
                    print("Checking if the site exists...")

                    if add_site == "0": continue

                    try:
                        requests.get(f"https://{add_site}", timeout=10)
                    except requests.exceptions.Timeout:
                        print("Connection timed out, retry or try again soon!")
                        continue

                    except requests.exceptions.ConnectionError:
                        print("Aborting! no internet connection :(")
                        continue

                    except (requests.exceptions.InvalidHeader, 
                            requests.exceptions.InvalidURL, 
                            requests.exceptions.InvalidSchema, 
                            requests.exceptions.MissingSchema) as e:

                        print("The site name was invalid, or a bad URL was inputted!")
                        print(f"Error) {e}")

                    except requests.exceptions.HTTPError as e:
                        print(f"A HTTPError occurred! \nError message) {e}")

                    else: print("Site is valid! continuing 𐔌՞. .՞𐦯")

                    # this is required as its converted to a list every restart
                    # because JSON doesnt have sets
                    if isinstance(self.valid_domains, list):
                        self.valid_domains = set(self.valid_domains)

                    self.valid_domains.add(add_site)
                    self.BnuyFileManager.saver()
                    print("Successfully added site!:3")
                    continue

                elif select == 2:
                    ui.site_printer(self.valid_domains)
                    del_loop = True
                    retry = False

                    while del_loop:
                        del_site = ui.del_site_select()
                        confirm_loop = True
                        try:
                            del_site = int(del_site)
                        except ValueError:
                            ui.general_exception("Please enter a number!")
                            continue

                        if del_site == 0:
                            confirm_loop = False
                            break

                        elif del_site not in range(1,len(self.valid_domains)+1):
                            ui.general_exception(f"Select 0-{len(self.valid_domains)}")
                            continue
                        # breaks if no errs occur
                        break

                    while confirm_loop:
                        confirm = ui.del_site_confirm(domains, del_site)

                        if confirm == "1": break

                        elif confirm == "0":
                            confirm_loop = False
                            break

                        else:
                            ui.general_exception("Select 0 or 1.")
                            continue

                    if confirm_loop is False: continue

                    self.valid_domains.remove(domains[del_site])
                    self.BnuyFileManager.saver()
                    print("Successfully deleted site from whitelist!")


            except ValueError:
                ui.general_exception()
                continue

    #### INTERNAL PLAYLIST EDITOR ####

    def internal_delete(self, num):
        for key, tupl in self.song_paths.items():
            # Folders are lists; therefore we can use .remove()
            if bnuyfolder.bnuuyfolder_check(tupl) and num in tupl:
                tupl.remove(num)

        del self.song_paths[num]

        self.BnuyFileManager.saver()


    #### METADATA PRINT AND COLLECTION ####
    def metadata_helper(self, path):
        count = 0
        metadata = {}

        invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".wma", ".lrc", ".py"}
        unsupported_ext = {".webm", ".mkv", ".it", ".avi", ".mov", ".mpg", ".mpeg", ".ts", ".flv", ".3gp"}

        for file in os.listdir(path):
            abs_path = os.path.join(path, file)

            key = max(metadata, default=0)+1

            if os.path.splitext(os.path.basename(file))[1] in invalid_ext:
                continue
            elif os.path.splitext(os.path.basename(file))[1] in unsupported_ext:
                continue

            data = mutagen.File(abs_path, easy=True)
            if data is None: continue
            else: metadata[key] = data
            print(f"{key}) {os.path.basename(file)}")

        print("\nNote: if a song is missing, the file format is likely unsupported.")

        return metadata


    #### WRITE SONG METADATA ####

    def metadata_handler(self, playlist, mode):
        ui.term_cleaner()
        tags = {
                "artist": "artist",
                "album": "album",
                "date": "date",
                "title": "title",
                "genre": "genre",
                }
        if mode == "add":
            enter_msg = "Enter the song you'd like to (re)write and the tag."
            data_choice = "Please enter the new data."

        else:
            enter_msg = "Enter the song and the tag you'd like to delete."
            data_choice = "Are you sure? enter anything to confirm."

        while True:
            try:
                print(f"""___________________________________________________________/\\
▼ Songs in {playlist[0]} ▼
""")
                metadata = self.metadata_helper(playlist[1])
                if len(metadata) == 0:
                    ui.special_exception("No songs in this playlist! :(")
                    continue

                write_select = ui.tag_printer(tags, enter_msg)

                values = write_select.split()

                if write_select == "0": return

                elif len(values) != 2: raise ValueError

                elif int(values[0]) not in range(1, len(metadata)+1):
                    ui.general_exception(f"Select a song from 1-{len(metadata)}")
                    continue

                else: num, tag = values

                selected_tag = tags.get(tag)

                if selected_tag is None:
                    ui.special_exception("Invalid tag, please enter a valid one.")
                    continue

                data = metadata.get(int(num))

                true = True
                retry = False
                try: 
                    curr_tag = data[f"{tag}"]
                except KeyError:
                    # KeyError occurs when no metadata exists
                    curr_tag = "No data available :("


                while true:

                    new_data = ui.enter_new_metadata(data_choice, tag, curr_tag)

                    if new_data == "0": 
                        true = False
                        retry = True
                        break
                    else: break

                if retry: continue

                if curr_tag != "No data available :(": old_data = data[f"{tag}"]

                else: old_data = "No data :("

                if mode == "add":
                    data[f"{tag}"] = [new_data]
                else:
                    try:
                        data.pop(f"{tag}")
                    except KeyError:
                        ui.special_exception("This key doesnt exist!")
                        continue
                try:
                    data.save()
                except (mutagen.MutagenError, OSError, PermissionError) as e:
                    ui.special_exception("An unknown error occurred! Full message may be below.")
                    print(e)
                if mode == "add":
                    print(f"Successfully changed {old_data} to {new_data}!")
                else:
                    print(f"Successfully deleted {old_data}!")


            except ValueError:
                ui.general_exception()
                continue

    #### METADATA SUBSETTINGS ####

    def metadata_settings(self):
        ui.term_cleaner()
        metadata_methods = {
                "add": self.metadata_handler,
                "del": self.metadata_handler,
                }

        while True:
            try:
                res = self.lib_print(local_only=True)
                keys = res.get("display_keys")

                selection = ui.metadata_main_menu()

                selected_stuff = selection.split()

                if selection == "0":
                    return

                if len(selected_stuff) != 2:
                    ui.special_exception("""
Please select the playlist, then what setting you'd like in the same message seperated by a space.""")
                    continue
                
                num = int(selected_stuff[0])
                cmd = selected_stuff[1]

                playlist = self.song_paths[keys[num][0]]
                if bnuyfolder.bnuuyfolder_check(playlist):
                    ui.special_exception("Please select a playlist and not a folder!")
                    continue
                metadata_methods[cmd](playlist, cmd)


            except (KeyError, ValueError):
                ui.general_exception("Select a playlist then the command.")
                continue

    #### SETTINGS / NON-MUSIC ####
    def settings(self):

        while True:
            try:

                if self.video: state = "Activated"
                else: state = "Deactivated"

                if self.gapless_toggle: gap_state = "Activated"
                else: gap_state = "Deactivated"

                choice = ui.main_settings(self.shuffl[1], self.ram_allocated, gap_state, state,)

                if choice == 0:
                    self.BnuyFileManager.saver()
                    break

                elif choice == 1:
                    """Shuffle toggler"""
                    # toggles shuffle's true/false
                    self.shuffl[0] = not self.shuffl[0]

                    if self.shuffl[0]:
                        self.shuffl[1] = "activated)  "
                    else:
                        self.shuffl[1] = "deactivated)"

                elif choice == 2:
                    """maximum RAM allocation"""
                    allocation_loop = True
                    while allocation_loop:
                        ram = ui.max_ram(self.ram_allocated)

                        if ram == "0": break
                        else: ram = int(ram)

                        self.ram_allocated = ram
                        print(f"Successfully allocated {ram}mB!")
                        break

                elif choice == 3:
                    """Gapless audio toggle"""
                    self.gapless_toggle = not self.gapless_toggle

                elif choice == 4:
                    """Video toggle"""
                    self.video = not self.video

                elif choice == 5:
                    self.site_whitelist_handler()

                elif choice == 6:
                    """Playlist sub settings"""
                    self.BnuyPlaylistManagement.playlist_settings()

                elif choice == 7:
                    """Metadata settings"""
                    self.metadata_settings()


                else:
                    raise KeyError
            except (ValueError, KeyError):
                ui.general_exception()

    #### INITIAL SETUP ####


    def file_setup(self):

        if not self.initialized:
            while True:
                try:
                    ui.first_setup_welcome()
                    choice = ui.adder_menu()

                    ## Main setup route
                    if choice in range(1, 5):
                        funct = self.adders[choice]
                        funct()
                        break

                    ## Skip route
                    elif choice == 0:
                        self.initializer()
                        break

                    ## No result found
                    else:
                        raise ValueError

                except ValueError:
                    ui.general_exception()
                    continue

    #### MAIN MENU ####


    def main_menu(self):

        self.BnuyFileManager.saver()
        ui.print_welcome()

        while True:
            """Menu printer"""
            # Iterates through main operations and prints
            try:
                choice = ui.print_main(self.main_operations, self.no_hint)

                """Help menu printer"""
                # Takes the hint section from the dict with name and num
                # then prints them together in a for loop
                if choice == "h":
                    ui.print_help(self.main_operations)
                    continue

                elif choice.lower() == "t":

                    # Toggles no hint off/on
                    self.no_hint = not self.no_hint

                    # writes to disk
                    self.BnuyFileManager.saver()
                    print("Successfully toggled.\n")
                    continue

                name, _, function = self.main_operations[choice]

                if name == "Exit": self.BnuyFileManager.saver()
                function()

            except KeyError:
                ui.general_exception()
                continue

    #### BNUUYSTART ####
    # Starts the main code loop
    def start_code(self):
        while True:
            if not self.initialized:
                self.file_setup()
            else:
                self.main_menu()
def start():
    bnuystart = BnuuyPlayer(mutagen_installed, db_ref)
