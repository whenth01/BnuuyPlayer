import os
import sys
import json
import time
import shutil
import difflib
import threading
import traceback
import subprocess
from datetime import timedelta

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

"""BadURL custom exception"""
# This is used in the YT_Dlp method if the user enters a wrong url
class BadURL(Exception):
    pass

"""Rare Errors exception"""
# Raised as a general exception for unlikely/rare events
class RareError(Exception):
    pass

#### JSON INIT ####


"""Initializes bnuuyplayer jsons when called"""
# NewStart creates the necessary bnuuyplayer jsons when called as(comment below)
# try: raise NewStart
# except NewStart as e: e.create_hist()
class NewStart(Exception):
    def __init__(self, path):
        super().__init__(path)

        self.hist_path = os.path.join(path, "BnuyPlayerHist.json")
        self.hist_backup1 = os.path.join(path, "BnuyBackup1.json")
        self.hist_backup2 = os.path.join(path, "BnuyBackup2.json")
        self.bulk_save = {}

    def create_hist(self):
        with open(self.hist_path, "w") as f:
            json.dump(self.bulk_save, f, indent=2)

        with open(self.hist_backup1, "w") as f:
            json.dump(self.bulk_save, f, indent=2)

        with open(self.hist_backup2, "w") as f:
            json.dump(self.bulk_save, f, indent=2)

#### MAIN BNUUYPLAYER CLASS ####

class BnuuyPlayer:

    def __init__(self, mutagen_installed):

        # Assigns the if mutagen is installed bool into self
        self.mutagen_installed = mutagen_installed

        # General config with placeholders, overwritten once processor is done.
        self.no_hint = False
        self.initialized = False
        self.shuffl = [False, "placeholder"]
        self.time_used = 0

        # Bulk save handles saving, song paths is used in playlist picker
        self.song_paths = {}
        self.bulk_save = {}

        # Pathways for various purpose, bnuy_path is the dir BnuuyPlayer is in.
        self.bnuy_path = os.path.dirname(__file__)
        self.hist_path = os.path.join(self.bnuy_path, "BnuyPlayerHist.json")
        self.hist_backup1 = os.path.join(self.bnuy_path, "BnuyBackup1.json")
        self.hist_backup2 = os.path.join(self.bnuy_path, "BnuyBackup2.json")
        self.keybind_dir = os.path.join(self.bnuy_path, "bnuybinds.conf")

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
                1: self.path_adder,
                2: self.folder_maker,
                3: self.song_searcher,
                4: self.yt_adder,
                }


        self.main_operations = {
               "1": ("Playlists", "Your library, your songs/playlists are here.", self.audio_funct),
               "2": ("Keybinds ","Music player keybinds.", self.binding_menu),
               "3": ("Settings ", "Your settings, this is where important functions are.", self.settings),
               "4": ("Stats & EasterEggs", "Your statistics(such as time used)", self.stats_display),
               "e": ("Exit", "Closes BnuuyPlayer", self.exity)
                } 


        self.valid_sentinels = {
               "Folder",
               "liked_songs",
               }
       

        """Method calls"""
        self.hist_creator()
        self.keybind_creator()
        counter = threading.Thread(target=self.time_counter, daemon=True)
        counter.start()
        sys.excepthook = self.bnuy_except_hook
        self.default_folders()
        self.start_code()

    #### BNUUYPLAYER TIME USED COUNTER ####

    """BnuuyPlayer time used"""

    def time_counter(self):
        while True:
            self.time_used += 1
            time.sleep(1)


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


    #### TERMINAL CLEARER ####

    def term_cleaner(self):
        os.system("cls" if os.name == "nt" else "clear")


    #### KEYBINDING MENU ####

    def binding_menu(self):
        """Keybind menu"""
        print("""
___________________________________________________________
▼ Keybinds ▼                                               |
                                                           |
q) Quit                                                    |
Q) Quit, but saves position                                |
l) Loop current song                                       |
m) Mute                                                    |
p / space ) Pause                                          |
P) show progress                                           |
i) Info                                                    |
< / >) Go backward/forward in the playlist                 |
[ / ]) -10% and +10% playback speed                        |
{ / }) Half/double playback speed                          |
Backspace) Reset playback speed to normal                  |
9 / 0) Vol +2 / -2                                         |
+ / -) skip 5s / back 5s                                   |
s / b) skip 30s / back 30s                                 |
G / F) Increase / decrease subtitle size                   |
___________________________________________________________|""")


    def adder_menu(self):
        # Asks the user for playlist method, returns to caller
        """Playlist method menu and choice returner"""
        choice = int(input("""
___________________________________________________________
▼ Playlist methods. ▼                                      |
                                                           |
1) Specify the path to your own folder.                    |
___________________________________________________________|
                                                           |
2) Allow BnuuyPlayer to make a folder automatically.       |
___________________________________________________________|
                                                           |
3) Allow BnuuyPlayer to search for a specified folder.     |
  (BnuuyPlayer can only search within the folder it's in.) |
___________________________________________________________|
                                                           |
4) Online download/stream.                                 |
  (Downloading will take up a chunk of storage.)           |
  (Streaming may introduce buffering.)                     |
  (Supported sites below.)                                 |
__________________________________________________         |
                                                  |        |
  ▼ Social media ▼                                |        |
    YouTube, TikTok, Reddit, FaceBook, Instagram  |        |
                                                  |        |
  ▼ Music and Audio ▼                             |        |
    bandcamp, audiomack, mixcloud, soundcloud     |        |
                                                  |        |
  ▼ Other ▼                                       |        |
    vimeo, dailymotion                            |        |
__________________________________________________|        |
                                                           |
___________________________________________________________|
                                                           |
0) Skip/back.                                              |
___________________________________________________________|

>>> """))
        self.term_cleaner()
        return choice

    ############# XTRA METHODS #############

    def stats_display(self):
        while True:
            try:
                choice = int(input("""
___________________________________________________________ 
▼ Statistics & EasterEggs ▼                                |
                                                           |
1) Amount of time you have been using Bnuuyplayer for      |
0) Return                                                  |
___________________________________________________________|

>>> """))
                match choice:
                    case 0: break

                    case 1:
                        time_elapsed = str(timedelta(seconds=self.time_used))
                        self.term_cleaner()
                        print(f"You have been using BnuuyPlayer for) {time_elapsed}")

                    case _: raise ValueError

            except ValueError: 
                self.term_cleaner()
                print("Invalid input!\n")
                continue



    ############# MAIN #############

    #### MUSIC PLAYER ####


    def audio_funct(self):
        while True:
            player = self.playlist_picker()
            # return from song menu picker
            if player is None: 
                self.term_cleaner()
                continue
            # return from main picker menu
            elif player == ("0", 0): return
            else: break

        if shutil.which("mpv") is None:
            print("Install MPV to access audio playback!")
            print("You can install MPV by reading bnuuyplayer's github README.md and folloeing the guide.")
            return

        print("")

        try:
            # lrc_thrd = threading.Thread(target=lrc_funct, daemon=True)
            # lrc_thrd.start()
            self.binding_menu()
            subprocess.run(player, check=True)

        except(subprocess.CalledProcessError) as e:
            print(f"Error occurred during playback! Error msg: {e}")


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
    #    self.term_cleaner()
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

    #### FOLDER CHECK ####

    def folder_check(self, tupl):

        if tupl[0] in self.valid_sentinels and not os.path.isdir(tupl[1]): return True
        else: return False

    #### DEFAULT FOLDER CREATOR ####

    # Creates a default internal folder if they dont exist
    def default_folders(self):
        liked_exists = False
        next_key = max(self.song_paths, default=0)+1

        for num, tupl in self.song_paths.items():
            if self.folder_check(tupl) and tupl[0] == "liked_songs":
                liked_exists = True

        if liked_exists is not True:
            self.song_paths[next_key] = ["liked_songs", "Liked songs",]


    #### LIBRARY PRINTER ####

    def lib_print(self, local_only=False, folder_only=False):
        local_countr = 0
        stream_countr = 0 
        full_countr = 0

        local_dict = {}
        stream_dict = {}
        folder_dict = {}

        # This is meant to be overwritten by the for loop.
        # The code will use it to know if there isnt any playlists
        num = None

        # checks if is stream is false, if it isnt then its likely online
        for num, tupl in self.song_paths.items():
            if self.folder_check(tupl):
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

        else:
            # Simply uses the last number from the for loop rather then incrementing
            if num is not None: full_countr = num
            else: full_countr = 0

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
            if self.folder_check(tupl): 
                folder_cache[len(folder_cache)+1] = (key, True)
            else:
                # filters out streamed entries when local_only is true
                if tupl[2] and local_only: continue

                display_keys[len(display_keys)+1] = (key, False)

        # This ensures that folders are always after flat playlists
        folder_keys = {i: v for i, v in enumerate(folder_cache.values(), start=len(display_keys)+1)}
        display_keys = display_keys | folder_keys

        #### Playlist printer ####

        if not folder_only:
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

        print("___________________________________________________________\\/")
        print("▼ BnuuyFolders ▼                                           /\\\n")

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

    #### LIKED FOLDER MANAGER ####

    def liked_manager(self, liked):
        songs = {}
        db_changed = False
        # We start at index 1 because liked is split by [2:]
        # and the for loop immediately adds 1
        curr_index = 1
        # Note; liked manager does not handle printing. Callers of it do
        print("""
___________________________________________________________/\\
▼ Liked songs ▼""")

        for path in liked[2:]:
            curr_index += 1
            if not os.path.isfile(path):
                db_changed = True
                found = False
                """Song search"""
                for root, dirs, files in os.walk(self.bnuy_path):

                    for file in files:
                        if os.path.basename(path) == file:
                            path = os.path.join(root, file)
                            liked[curr_index] = path
                            found = True

                            break 

                    if found: 
                        songs[len(songs)+1] = path
                        break

                if found is False: 
                    print("A liked song disappeared; was it deleted or moved out?")
                    print(f"Missing song) {os.path.basename(os.path.splitext(path)[0])}")
                    liked.remove(path)
                    continue

            else: songs[len(songs)+1] = path

        if db_changed:
            self.saver()

        return songs
        

    #### FOLDER MANAGER ####

    def folder_manager(self, tupl):
        while True:
            disp_keys = {}
            try:

                self.term_cleaner()
                name = tupl[1]

                if tupl[0] == "liked_songs":
                    songs = self.liked_manager(tupl)
                    return songs

                print(f"""
___________________________________________________________/\\ 
▼ Playlists in {name} ▼""")

                # Folders contain keys of playlists rather then full tuples.
                for num in tupl[2:]:
                    disp_keys[len(disp_keys)+1] = num

                for key, og_key in disp_keys.items():
                    name, path, is_stream, function = self.song_paths[og_key]
                    if is_stream:
                        print(f"{key}) {name} (Online stream)")
                    else: 
                        print(f"{key}) {name}")

                # If the folder is empty
                if len(tupl) == 2: print("No playlists in the folder.")

                choice = int(input("""
___________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))
                self.term_cleaner()
                if choice == 0: return None

                else:
                    res = {
                         "selected": self.song_paths[disp_keys[choice]],
                         "key": disp_keys[choice],
                          }
                    return res


            # temp debug code
            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input. \n")
                continue

    #### FILE.MOVER ####
    def move_file(self, path):
        while True:
            try:
                res = self.lib_print(local_only=True)

                library = res.get("full_dict")
                display_keys = res.get("display_keys")

                selection = int(input("""
___________________________________________________________\\/
Please select the location you'd like to move the song to. |
                                                           |
0) Return.                                                 |
___________________________________________________________|

>>> """))

                if selection == 0: break 

                if self.folder_check(library[display_keys[selection][0]]):
                    raise ValueError

                _, dest_path, is_stream, _ = library[display_keys[selection][0]]

                if is_stream:
                    self.term_cleaner()
                    print("Invalid input, wrong number entered!")
                    continue

                confirm = int(input(f"""
___________________________________________________________ 
Are you sure?                                              /\\
Source) {path}
Destination) {dest_path}
___________________________________________________________\\/
▼ Commands ▼                                               |
                                                           |
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|

>>> """))
                if confirm == 1:
                    lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
                    lrc_path = os.path.join(os.path.dirname(path), lrc_file)
                    if os.path.isfile(lrc_path):
                        try:
                            shutil.move(lrc_path, dest_path)
                        except shutil.Error:
                            self.term_cleaner()
                            print("Lyric file already exists in that directory:( skipping..")
                            continue
                    try:
                        shutil.move(path, dest_path)
                    except shutil.Error:
                        self.term_cleaner()
                        print("File already exists in that directory :( Canceling..")
                        continue

                    print("Successfully moved file!")

                elif confirm == 0: break 

                else: raise ValueError

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input :(")
                continue

    #### CMD HANDLER ####

    def cmd_handler(self, params):
        cmd = params.get("cmd")
        path = params.get("path")

        match cmd:

            case "l":
                """Like a song"""
                success = False
                for _, tupl in self.song_paths.items():
                    if self.folder_check(tupl) and tupl[0] == "liked_songs":
                        tupl.append(path)
                        self.saver()
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
                    print("Cannot delete streamed songs from disk.")
                    return
                else:
                    while True:
                        self.term_cleaner()
                        confirm = input(f"""
__________________________________________________________/\\
Are you sure? you are deleting) {os.path.basename(os.path.splitext(path)[0])}
                                                          \\/
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|

>>> """)

                        if confirm == "1": break 

                        elif confirm == "0": 
                            self.term_cleaner()
                            return 

                        else:
                            self.term_cleaner()
                            print("Invalid input, enter 1 or 0")
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
                        select = int(input(f"""
___________________________________________________________\\/
Select the playlist you'd like to copy the song to.        /\\
Selected file) {os.path.basename(os.path.splitext(path)[0])}
                                                           \\/
0) Return                                                  |
___________________________________________________________|

>>> """))

                        if select == 0:
                            self.term_cleaner()
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

                            elif self.folder_check(selected):
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
                                self.term_cleaner()
                                print(message)
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
                                self.term_cleaner()
                                print("Successfully copied file!")
                                continue

                            except shutil.SameFileError:
                                self.term_cleaner()
                                print("File already exists in the destination!")
                                continue

                    except ValueError:
                        self.term_cleaner()
                        print("Invalid input :(")
                        continue

                    except TypeError:
                        self.term_cleaner()
                        print("Invalid number.")
                        continue

            case "p":
                """Play song"""
                return path

            case _:
                self.term_cleaner()
                print("Invalid input! D:")
                return

    #### SEARCH LIBRARY ####

    def investibun_search(self):
        while True:
            try:
                search_select = input("""
___________________________________________________________
Search bnuuyplayer for a song/playlist.                    |
                                                           |
1) Search for songs                                        |
2) Search for Playlists (note: streamed songs are here)    |
0) Return                                                  |
___________________________________________________________|

>>> """)

                if search_select == "0":
                    self.term_cleaner()
                    return

                self.term_cleaner()
                search_query = input("""
___________________________________________________________ 
Enter the name of what you'd like to find.                 |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """)

                if search_query == "0":
                    self.term_cleaner()
                    return

                entries = {}
                songs = []
                song_handler = False
                playlist_handler = False

                for key, tupl in self.song_paths.items():
                    if self.folder_check(tupl) is True: continue

                    else: name, path, is_stream, _ = tupl

                    if search_select == "2": 
                        """Playlist route"""
                        for num in entries.keys():
                            if name == num:
                                name = f"{name} (2)"
                        entries[name.lower()] = path, is_stream, len(entries)+1, key
                        playlist_handler = True

                    elif search_select == "1":
                        """Songs route"""
                        if os.path.isdir(path):

                            compiler = []
                            for name in os.listdir(path):
                                split = os.path.splitext(name)[0].lower()
                                compiler.append(split)

                            entries[key] = compiler
                            songs += compiler
                            song_handler = True

                        else: continue

                    else:
                        self.term_cleaner()
                        print("Invalid input.")
                        break

                else:

                    # The reason why theyre seperate is that songs need to be unpacked
                    # because os.listdir() returns a list of strings
                    if song_handler:

                        search = set(difflib.get_close_matches(search_query.lower(), songs, n=8, cutoff=0.3))
                    else:
                        search = set(difflib.get_close_matches(search_query.lower(), entries, n=8, cutoff=0.3))

                    self.term_cleaner()
                    if playlist_handler:
                        """Playlist printer"""
                        print("""
___________________________________________________________
▼ Closest playlist matches ▼                              /\\\n""")

                        for name, (path, is_stream, num, og_key) in entries.items():

                            if is_stream and name in search: 
                                print(f"""{num}) {name} (Online stream.)
(located at {og_key})\n""")

                            elif name in search: 
                                print(f"""{num}) {name}
(located at {og_key})\n""")

                        if len(search) == 0:
                            print("No matches found! :(")
                    else:
                        """Song paths printer"""

                        print("""
___________________________________________________________ 
▼ Closest song matches ▼                                  /\\\n""")
                        for key, names in entries.items():
                            playlist_name, _, _, _, = self.song_paths[key]
                            for song_name in names:
                                if song_name in search:
                                    print(f"""{song_name}
Located at
Playlist name) {playlist_name}
Playlist key) {key}\n""")

                    print("__________________________________________________________\\/")

            except ValueError:
                self.term_cleaner()
                print("Invalid input! :(")
                continue

    #### METADATA COMPILER & BACKEND ####

    def bulk_helper(self, params, mode, dest_path):

        processed_files = 0

        for num, (metadata, path, key) in params.items():
            if not os.path.isdir(dest_path):
                print("Destination path was deleted, please select a new playlist!")
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
                selection = int(input("""
___________________________________________________________\\/
Please select a playlist to move the song(s) into.         |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                if selection == 0:
                    self.term_cleaner()
                    return
                
                keys = res.get("display_keys")
                selected_playlist = self.song_paths[keys[selection][0]]

                # is folder check
                if keys[selection][1]:
                    self.term_cleaner()
                    print("Can not select a folder, please select a playlist.")
                    continue
                # Stream check
                elif selected_playlist[2]: raise ValueError

                dest_path = selected_playlist[1]

                while True:
                    confirm = input(f"""
___________________________________________________________
Are you sure?                                             /\\
You are moving {len(params)} file(s) (not including lyric files)
into {selected_playlist[0]}
                                                          \\/
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|

>>> """)

                    if confirm == "0":
                        self.term_cleaner()
                        break
                    elif confirm == "1":
                        self.term_cleaner()
                        amount_moved = self.bulk_helper(params, "move", dest_path)

                        print(f"Moved {amount_moved} files!:3")
                        return

                    else:
                        self.term_cleaner()
                        print("Invalid input.")
                        continue

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input, please select a playlist")
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

                dest_select = int(input("""
___________________________________________________________\\/
Select a playlist to copy the files into.                  |
(note: This may take up alot of storage!)                  |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                if dest_select == 0:
                    self.term_cleaner()
                    return

                keys = res.get("display_keys")

                selected_playlist = self.song_paths[keys[dest_select][0]]
                # folder check
                # keys hold a is folder value at index 1
                if keys[dest_select][1]:
                    self.term_cleaner()
                    print("Cannot select a folder :(, please select a playlist!")
                    continue

                # stream check
                elif selected_playlist[2]: raise ValueError

                confirm_loop = True
                while confirm_loop:
                    self.term_cleaner()
                    confirm = input(f"""
__________________________________________________________/\\
Are you sure? you are copying {len(params)} files (excluding lyric files)
Copy size in megabytes) {int(copy_size_mb)}
Copy size in gigabytes) {int(copy_size_gb)}
into the playlist) {self.song_paths[keys[dest_select][0]][0]}

1) Continue                                               \\/
0) Return                                                  |
___________________________________________________________|

>>> """)

                    if confirm == "1": pass

                    elif confirm == "0":
                        self.term_cleaner()
                        confirm_loop = False
                        break

                    else:
                        self.term_cleaner()
                        print("Invalid input, pick 1 or 0.")
                        continue

                
                    name, dest_path, _, _, = selected_playlist

                    amount_copied = self.bulk_helper(params, "copy", dest_path)

                    print(f"Copied {amount_copied} files!:3")
                    return


            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input, please select a playlist")
                continue

    #### METADATA BASED BULK DELETE ####

    def bulk_delete(self, params):
        while True:
            try:
                confirm = int(input(f"""
___________________________________________________________
Are you sure? This is permanent.                          /\\
You are deleting {len(params)} files(excluding lyric files).
                                                          \\/
1) Continue                                                |
0) Return                                                  |
___________________________________________________________|
                      
>>> """))


                if confirm == 1:
                    # spoofing the dest path to make it fit in
                    amount_deleted = self.bulk_helper(params, "delete", self.bnuy_path)
                    print(f"Deleted {amount_deleted} files.")
                    return 

                elif confirm == 0:
                    return

                else: raise ValueError

            except ValueError:
                self.term_cleaner()
                print("Invalid input! select 0 or 1.")
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
        unsupported_ext = {".webm", ".mkv", ".it", ".avi", ".mov", "mpg", ".mpeg", ".ts", ".flv", ".3gp"}
        # valid search tags
        tags = {
            "artist": "artist",
            "title": "title",
            "album": "album",
            }

        while True:
            try:
                print("""
___________________________________________________________ 
▼ Advanced search doesnt support ▼                         |
                                                           |
.webm .mkv .mod .xm .s3m .it .mid .midi                    |
.avi .mov .mpg .mpeg .ts .flv .3gp                         |
And advanced search doesnt look through streamed entries.  |
___________________________________________________________|""")

                selection = input("""
___________________________________________________________
Enter a tag and what you'd like to search.                 |
E.g) artist [your query]                                   |
___________________________________________________________|
▼ Tags ▼                                                   |
                                                           |
artist                                                     |
album                                                      |
title                                                      |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """)

                values = selection.split()
                if values[0] == "0": return

                elif len(values) < 2: raise ValueError

                else:
                    self.term_cleaner()
                    tag = tags.get(values[0])

                    if tag is None: raise ValueError

                    # reconstructs the string 
                    # 0 is the tag (as seen above)
                    query = " ".join(values[1:])
                    results = {}
                    # this starts by searching playlists in self.song_paths 
                    # for their metadata
                    for num, tupl in self.song_paths.items():
                        if self.folder_check(tupl): continue
                        
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
                                    if check < 0.3: 
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
                            print("""
___________________________________________________________
▼ Closest results ▼                                       /\\""")
                            for num, res in results.items():
                                """tuple collection"""
                                data_dict = res[0]
                                song_path = res[1]
                                location = res[2]
                                """metadata collection"""
                                artist = data_dict.get("artist")
                                title = data_dict.get("title")
                                album = data_dict.get("album")

                                print(f"""
Artist(s): {artist}
Title: {title}
Album: {album}
Playlist name: {self.song_paths[location][0]} 
Playlist key: {location}""")


                            choice = input(f"""
__________________________________________________________\\/
1) Move every result into a playlist (may take some time.)|
2) Copy every result into a playlist (will take storage)  |
3) Delete every result. (may take some time)              |
4) Play every result                                      |
0) Return                                                 |
__________________________________________________________|

>>> """)

                            funct = bulk_methods.get(choice)
                            if choice == "0": break

                            elif funct is None: 
                                self.term_cleaner()
                                print("Invalid input, select a number between 0-3")
                                continue

                            else: 
                                self.term_cleaner()
                                funct(results)
                                break

            except ValueError:
                self.term_cleaner()
                print("Invalid input.")
                print("Read BnuuyPlayer's README.md help section.")
                continue

            except IndexError:
                self.term_cleaner()
                print("Invalid input.")
                continue

    #### LYRIC DOWNLOAD ####

    def lrc_dl(self):

        while True:
            confirm = input("""
___________________________________________________________
Are you sure? this may take a while.                       |
                                                           |
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|

>>> """)

            if confirm == "1": break
            elif confirm == "0": return
            else:
                self.term_cleaner()
                print("Invalid input! select 1 or 0.")
                continue

        # Downloads lyrics for existing songs
        for _, tupl in self.song_paths.items():
            # folder check
            if self.folder_check(tupl): continue
            # is stream check
            if tupl[2]: continue

            name, path, _, _, = tupl

            print(f"Beginning download for {os.path.basename(path)}")

            d = {"status": "finished", 
                 "filename": "placeholder",
                 "filepath": path,
                 "info_dict": {},}

            for file in os.listdir(path):

                metadata = mutagen.File(os.path.join(path, file), easy=True)

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
                d["filename"] = file

                self.yt_hook(d)



    #### PLAYLIST PICKER ####

    def playlist_picker(self):
        while True:

            try:

                countr = 0

                res = self.lib_print(local_only=False)
                display_keys = res.get("display_keys")

                choice = input("""__________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           |
s) Search                                                  |
as) Advanced Search (may be slow)                           \\
dl) Download lyrics for existing songs(note: this relies on metadata)
0) back                                                     /
___________________________________________________________|

>>> """)

                self.term_cleaner()
                countr = 0
                tmp_song = {}

                # causes audio funct to raise ValueError, causing a return to main menu
                if choice == "0":
                    self.term_cleaner()
                    return choice, countr

                elif choice.lower() == "s":
                    self.investibun_search()
                    continue

                elif choice.lower() == "as":
                    self.advanced_investibunny()
                    continue

                elif choice.lower() == "dl":
                    self.lrc_dl()
                    continue

                else: choice = int(choice)

                # defines values that local song picker requires
                choice = display_keys[choice][0]
                
                tupl = self.song_paths[choice]
                liked_handler = False

                if self.folder_check(tupl):
                    res = self.folder_manager(tupl)

                    if res is not None:
                        values = res.get("selected")

                        if values is None: 
                            liked_handler = True
                            path = res
                            is_stream = True

                    else: continue

                    # regular route
                    if values is not None:
                        name, path, is_stream, function = values

                else: name, path, is_stream, function = tupl
                if not liked_handler:
                    if not os.path.isdir(path) and is_stream is False:
                        self.term_cleaner()
                        print("The original folder is missing, did you move it or delete it?")
                        print("Deleting playlist for stability..")
                        self.internal_delete(choice)
                        continue

                picker_skip = False
                # prints every local song in current song path playlist
                # splits the extension from songname, compares to invalid ext
                # if it is in invalid ext it skips, otherwise print
                if liked_handler is False and is_stream is False:
                    invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".wma", ".lrc"}

                    for song in os.listdir(path):
                        filename, ext = os.path.splitext(song)

                        if ext not in invalid_ext:
                            filepath = os.path.join(path, song)
                            countr += 1
                            print(f"{countr}) {filename}")
                            tmp_song[countr] = filepath

                # liked handler printer
                elif liked_handler is True:
                    disp_keys = {}
                    for num, song in res.items():
                        disp_keys[len(disp_keys)+1] = num, song

                    for key, (og_key, song) in disp_keys.items():
                        print(f"{key}) {os.path.basename(os.path.splitext(song)[0])}")
                        tmp_song[og_key] = song

                else:
                    # This prevents the second error message below from going off
                    tmp_song[len(tmp_song)+1] = ""
                    print(
                    "Warning: Individual song picking is unsupported for streaming due to technical limitations."
                    )
                    picker_skip = True

                # Checks if the song path dict is empty, otherwise act normal
                selection_loop = True
                restart = False
                while selection_loop:

                    if len(tmp_song) < 1:
                        self.term_cleaner()
                        print("Playlist is empty.\n")
                        continue
                    if not picker_skip:
                        choice = input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Play the whole playlist                                 |
0) Back                                                    |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
(num) l — Like a song. Gets added to liked songs folder.   |
(num) d — Delete a song from disk.                         |
(num) m — Move a song to a new playlist.                   |
(num) c — Copy a song file to a new playlist.              | 
(num) p — Play a single song.                              |
___________________________________________________________|

>>> """)

                    else: 
                        choice = "1"
                        break

                    self.term_cleaner()
                    tmp_choice = choice.split()

                    if len(tmp_choice) == 2:
                        num = int(tmp_choice[0])
                        cmd = tmp_choice[1]
                        path = tmp_song[num]
                        params = {
                            "num": num,
                            "cmd": cmd,
                            "path": path,
                            "songs": tmp_song,
                            }

                        res = self.cmd_handler(params)
                        # res is only not none when a indiv song is to be played
                        if res is None:
                            for num, file in tmp_song.items():
                                print(f"{num}) {os.path.basename(os.path.splitext(file)[0])}")
                            continue

                        else:
                            liked_handler = False
                            break

                    else: 
                        choice = int(choice)
                        break

                if restart: continue

                # Returns none which loops the code in self.audio_funct
                if choice == 0: return None

                elif choice == 1 or liked_handler is False:
                    self.term_cleaner()
                    # automatically moves on, no need for extra logic

                else: raise ValueError 

                if not liked_handler:
                    path = [path]
                else: path = [*path.values()]

                player = [
                    "mpv",
                    *path,
                    f"--input-conf={self.keybind_dir}",
                    "--profile=fast",
                    "--no-video"
                    ]


                # f"--input-ipc-server={self.bnuy_path}/.mpv_socket"
                # saving this here for when i have a laptop/pc.

                if self.shuffl[0]:
                    player.append("--shuffle")

                self.term_cleaner()

                return player

            except (KeyError, ValueError):
                self.term_cleaner()
                print("Invalid input.")
                continue


            except Escape:
                continue


    #### CORRUPTED HIST CREATOR ####

    def corr_backup(self):
        """Recovers backups for the user to manually recover"""

        success_reads = 1

        # Each successful read adds 1
        # if 1 failed it checks which failed, and rewrites with err msg

        while success_reads < 4:
            try:

                if success_reads == 1:
                    with open(self.hist_path) as f:
                        main = f.read()
                    success_reads += 1

                elif success_reads == 2:
                    with open(self.hist_backup1) as f:
                        backup1 = f.read()
                    success_reads += 1

                else:
                    with open(self.hist_backup2) as f:
                        backup2 = f.read()
                    success_reads += 1

            except(FileNotFoundError,OSError):

                if success_reads == 1: main = "UNREADABLE OR DELETED"

                elif success_reads == 2: backup1 = "UNREADABLE OR DELETED"

                else: backup2 = "UNREADABLE OR DELETED"

                success_reads += 1  



        print(f"""MAIN HIST: {str(main)}

BACKUP1: {str(backup1)}

BACKUP2: {str(backup2)}""")

        input("""\nYour lib was corrupted! Screenshot/copy the previous or this message before continuing.


This means your entire library was likely corrupted. (the folders themselves are likely fine.)


You can rebuild your library via copy/pasting the paths and urls, then using path adder and stream/downloader if any remain.

BnuuyPlayer will backup the previous json and has just printed the json's contents to allow you to manually recover them if any remnant exists.

Enter any key to continue.""")


        num = 0

        while True:

            """Backs up all available corrupted backups"""
            corr_path = os.path.join(self.bnuy_path, f"CorruptedBnuuyHist_{num}.json")
            corr_backup1 = os.path.join(self.bnuy_path, f"CorruptedBnuuyBackup_{num}.json")
            corr_backup2 = os.path.join(self.bnuy_path, f"CorruptedBnuuyBackup2_{num}.json")

            json_checker = os.path.isfile(corr_path)
            backup_checker = os.path.isfile(corr_backup1)
            backup_checker2 = os.path.isfile(corr_backup2)

            if json_checker or backup_checker or backup_checker2:
                num += 1
                continue

            # Checks if file exists, if it does it rewrites
            else:
                if os.path.isfile(self.hist_path):
                    os.rename(self.hist_path, corr_path)

                if os.path.isfile(self.hist_backup1):
                    os.rename(self.hist_backup1, corr_backup1)

                if os.path.isfile(self.hist_backup2):
                    os.rename(self.hist_backup2, corr_backup2)
                break

    #### HIST LOADER ####

    def loader_bunny(self, num):
        hists = {1: self.hist_path,
                 2: self.hist_backup1,
                 3: self.hist_backup2,}
        try:
            # attempts to load all hists, an error increments num
            # incrementing is done by processor
            path = hists[num]

            with open(path) as f:
                self.bulk_save = json.load(f)

        except(json.JSONDecodeError, AttributeError, SyntaxError, FileNotFoundError):
            # Returns back to processor to let it do the job of incrementing
            pass

    #### BUNNY RECOVERER ####

    def recovery_bunny(self, values):
        recov_attempts = 1

        recovered = {}
        failed = {}
        for key, method in values.items():


            while True:

                if self.bulk_save.get(key) is not None:

                    # Attempts to reassign the attribute to the newest file.
                    setattr(self, method, self.bulk_save.get(key))
                    recovered[key] = method
                    recov_attempts = 1
                    break

                elif recov_attempts == 4:

                    failed[key] = method
                    # Resets back to 1
                    recov_attempts = 1
                    break 

                else: 
                    self.loader_bunny(recov_attempts)
                    recov_attempts += 1 
                    continue

        return failed, recovered



    #### LOADSAVE FILE LOADER ####

    def processor(self):
        recov_attempts = 1

        self.loader_bunny(recov_attempts)

        # Dict keys match the JSON keys.
        lookup_registry = {
        "0": "song_paths",
        "1": "initialized",
        "2": "no_hint",
        "3": "shuffl",
        "4": "time_used",
        }

        failed_keys = {}

        for key, item in lookup_registry.items():
            # equivalent to e.g: self.song_paths = self.bulk_save.get("0")
            # setattr is required as self.item = ... would create an attribute 
            # named item rather than interacting with the actual items.
            setattr(self, item, self.bulk_save.get(key))

            # Checks for corrupted or failed keys, compiles to failed_keys
            if self.bulk_save.get(key) is None:
                failed_keys[key] = item


        """Song paths recoverer"""
        # this is used to make self.shuffl a list as a flag
        make_list = False


        if len(failed_keys) >= recov_attempts:

                failed, recovered = self.recovery_bunny(failed_keys)

                if "0" in failed:
                    """Song paths check"""
                    self.corr_backup()
                    self.song_paths = {}
                    self.initialized = False
                    self.no_hint = False
                    self.shuffl = [False, "placeholder"]
                    self.time_used = 0
                    return

                make_list = False

                if "4" in failed: 
                    """Time used check"""
                    print("Your time stat was corrupted/unrecoverable, setting to 0.")
                    self.time_used = 0

                solved = []
                for key, method in failed.items():
                    while True:
                        if key == "1" or key == "2" or key == "3":
                            if key == "3": 
                                """Shuffl check"""
                                make_list = True

                            choices = {
                                "1": True, 
                                "2": False,
                                }

                            select = input(f"""A JSON entry was corrupted!
Entry) {method}

1) Set it to the True/on position.
2) Set it to the False/off position.""")

                            self.term_cleaner()

                            selected_bool = choices.get(select)

                            if selected_bool is None:
                                self.term_cleaner()
                                print("Invalid input!\n")
                                continue

                            if make_list:
                                selected_bool = [selected_bool, "placeholder"]
                                make_list = False

                            setattr(self, method, selected_bool)
                            solved.append(key)
                            break

                        else: break
                # Cleans up the failed keys
                for key in solved:
                    del failed[key]


        tmp_handler = {}
        err_paths = {}
        del_dict = {}

        invalid_countr = 0
        
        """Playlist corr/valid sorter"""
        # Attempts to recover playlists, if it fails
        # it adds 1 to invalid countr, then adds it to err paths
        # if the playlist is recovered successfully, its put into tmp handler
        for num, tupl in self.song_paths.items():

            # This doesnt require integrity checks as it stores keys.
            if self.folder_check(tupl):
                tmp_handler[num] = tupl

            elif len(tupl) == 3:
                name, path, is_stream = tupl

                # Sorts working and non working paths, bad ones are DELETED
                if os.path.isdir(path) or is_stream is True:
                    tmp_handler[num] = (name, path, is_stream, self.audio_funct)
                else:
                    print(f"Found a invalid save at {path} \ndeleting to prevent bugs..")
                    del_dict[num] = num, tupl

            else:
                invalid_countr += 1
                print(f"""\nFound invalid save path, was the JSON edited/corrupted?
Found {invalid_countr} invalid save paths.
Corrupted/edited path) {tupl}""")

                err_paths[len(err_paths) + 1] = tupl

        if len(err_paths) > 0:
            print(f"Invalid saves list; {err_paths}")

        self.song_paths = tmp_handler # pushes recovered playlists back into the dict
        # Note: invalid songs are already scrubbed, theyre not included in tmp_handler

        tmp_db = {}
        # converts json string keys back into integers
        for key, tupl in self.song_paths.items():

            try:
                key = int(key)
            except ValueError:
                print(f"Invalid key was found, was the json modified?")
                print(f"Deleting the entry at key {key} for stability.")
                continue

            tmp_db[key] = tupl

        self.song_paths.clear()
        self.song_paths.update(tmp_db)


    #### PERSISTENT HIST CREATOR ####

    def hist_creator(self):
        """Hist creator/checker/loader"""
        # Pulled from self, checks if the jsons actually exists.
        # If it doesnt exist, raise NewStart
        try:
            if not os.path.isfile(self.hist_path) and not os.path.isfile(self.hist_backup2) and not os.path.isfile(self.hist_backup1): 
                raise NewStart(self.bnuy_path)

            self.processor()

        except NewStart as e:
            e.create_hist()


    ############# MAIN FOLDER/SETUP AREA #############


    #### HISTORY ADDER ####


    def saver(self):
        tmp_handler = {}
        self.bulk_save = {}
        tmp_path = os.path.join(self.bnuy_path, "BnuyPlayerHist.json.tmp")

        """Save compiler"""
        # Compiles every playlist into a temp dict to be saved.
        for num, tupl in self.song_paths.items():

            if self.folder_check(tupl):
                tmp_handler[num] = tupl

            else:
                (name, combined, is_stream, _) = tupl
                tmp_handler[num] = (name, combined, is_stream)

        # Assigns a local version of self.song_paths with audio_funct stripped
        save_song_paths = tmp_handler

        """Bulk save build"""
        # Compiles bulk save.
        self.bulk_save[0] = save_song_paths
        self.bulk_save[1] = self.initialized
        self.bulk_save[2] = self.no_hint
        self.bulk_save[3] = self.shuffl
        self.bulk_save[4] = self.time_used

        successful_saves = 0
        """Atomic write to disk"""
        # Writes the tmp handler into the disk, first to hist_path, then backups
        # Ensures corruption cant occur via os.replace and backups
        # Uses successful saves to make sure all saves were uncorrupted

        try:


            with open(tmp_path, "w") as f:
                json.dump(self.bulk_save, f, indent=2)
            os.replace(tmp_path, self.hist_path)
            successful_saves += 1


            # Reads from main hist, write to backup1
            with open(self.hist_path, "r") as mainhist, open(self.hist_backup1, "w") as backup1:
                backup1.write(mainhist.read())
            successful_saves += 1

            # If it was successful, read backup1, write it to backup2
            if os.path.isfile(self.hist_backup1):
                with open(self.hist_backup1, "r") as backup1, open(self.hist_backup2, "w") as backup2:
                    backup2.write(backup1.read())
                successful_saves += 1

        except(FileNotFoundError, OSError) as e:
            if successful_saves == 0:
                print(f"Device ERROR during save, BnuuyPlayer is unable to work properly! Error message: \n\n{e}")

            else:
                self.corr_backup()




    #### EXCEPT HOOK ####

    def bnuy_except_hook(self, exctype, value, traceback):
        """Custom messages for exceptions"""

        # Specific error handling to make specific cases not crash the code.
        if exctype == KeyboardInterrupt: 
            print("\n\nTurning off.. Thank you for using BnuuyPlayer!")
            self.saver()
            sys.exit()

        elif exctype == IsADirectoryError:
            print("""IsADirectoryError occurred!
This means you likely named a folder after one of BnuuyPlayer's jsons.

Please rename the folder or delete it to use BnuuyPlayer.""")
            sys.exit()
        else:
            sys.__excepthook__(exctype, value, traceback)


    #### EXIT FUNCT ####

    def exity(self):
        sys.exit()


    #### PLAYLIST/PATH ADDER ####


    def path_adder(self):
        self.term_cleaner()
        is_stream = False
        while True:
            try:
                path_input = input("""
___________________________________________________________
▼ Valid file paths ▼                                       |
                                                           |
MacOS: /users/<your_username>/...                          |
Linux: /home/<your_username>/...                           |
Android: /storage/emulated/0/...                           |
Windows: C:\\users\\<your_username>\\...                      |
___________________________________________________________|
                                                           |
These are how your device sees your folders/files.         |
A folder named "Synth" on android in the Home dir would be |
/storage/emulated/0/synth                                  |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Back                                                    |
___________________________________________________________|

Please input a path to a folder.

>>> """)

                if path_input == "0":
                    break

                """Folder validator"""
                is_playlist_path = os.path.isdir(path_input)

                # Validates that the folder exists
                if not is_playlist_path:
                    self.term_cleaner()
                    print("\nDirectory doesn't exist, or you made a typo.")
                    continue

                # If the folder exists, keep going
                else:
                    self.term_cleaner()
                    while True:
                        name_choice = input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Create a display name.                                  |
2) Use the folder name.                                    |
___________________________________________________________|

>>> """)
                        if name_choice == "1":
                            playlist_name = input("""\nEnter the display name.
>>> """)
                            break

                        # Assigns the folder the base name
                        elif name_choice == "2":
                            playlist_name = os.path.basename(path_input)
                            break

                        else:
                            print("Invalid choice!")
                            continue

                    # Save to song paths, write to disk, flip initializer if false
                    next_key = max(self.song_paths, default=0)+1 

                    self.song_paths[next_key] = (playlist_name, path_input, is_stream, self.audio_funct)

                    self.saver()
                    self.term_cleaner()
                    print("Playlist successfully added!")

                    self.initializer()

                    path_input = input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Add one more path.                                      |
0) Return to BnuuyPlayer main menu                         |
___________________________________________________________|

>>> """).lower()

                if path_input == "0":
                    break
                elif path_input == "1":
                    continue
                else:
                    raise ValueError

            except ValueError:
                self.term_cleaner()
                print("Invalid input.\n")
                continue


    #### ADD/CREATE FOLDER ####
    # note: this is separate from bnuuyplayer's internal folders
    # and creates physical folders in current directory
    def folder_maker(self):
        is_stream = False
        self.term_cleaner()
        while True:
            try:

                folder_name = input("""
___________________________________________________________
Continue to let BnuuyPlayer to make a folder.              |
                                                           |
1) Continue                                                |
0) Back                                                    |
___________________________________________________________|

>>> """)

                if folder_name == "1":
                    self.term_cleaner()
                    folder_name = input("""
___________________________________________________________
What would you like to name the playlist?                  |
___________________________________________________________|

>>> """)

                    song_path = os.path.join(self.bnuy_path, folder_name)
                    os.makedirs(song_path)
                    next_key = max(self.song_paths, default=0)+1
                    self.song_paths[next_key] = (folder_name, song_path, is_stream, self.audio_funct)
                    self.saver()

                    self.term_cleaner()
                    print(f"""\nSuccessfully created.
Path to the new playlist folder) {song_path}

You can add any song to the newly created playlist.""")

                    self.initializer()

                    break

                elif folder_name == "0":
                    break

                else:
                    self.term_cleaner()
                    raise ValueError

            except FileExistsError:
                self.term_cleaner()
                print("\nFolder or file already exists.")
                continue

            except OSError:
                self.term_cleaner()
                print("""
___________________________________________________________
Unknown Error. You likely use an invalid character/name.   |
___________________________________________________________|
                                                           |
Invalid character/name list                                |
                                                           |
___________________________________________________________|
Windows:                                                   |
< > : - " / \\ | ? *                                        |
                                                           |
CON, PRN, AUX,                                             |
NUL COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9   |
LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9       |
                                                           |
0-31 (ASCII control characters)                            |
                                                           |
Names also cannot end in a dot or space.                   |
                                                           |
___________________________________________________________|
                                                           |
Linux:                                                     |
0 (NULL byte)                                              |
/                                                          |
. (special name referring to current directory)            |
.. (special name referring to parent directory)            |
                                                           |
___________________________________________________________|
                                                           |
macOS:                                                     |
:                                                          |
/                                                          |
                                                           |
___________________________________________________________|
                                                           |
Android:                                                   |
< > : - " / \\ | ? *                                        |
\\n                                                         |
0-31 (ASCII control characters)                            |
                                                           |
___________________________________________________________|
                                                           |
BnuuyPlayer:                                               |
BnuyPlayerHist.json                                        |
BnuyBackup1.json                                           |
BnuyBackup2.json                                           |
bnuybinds.conf                                             |
                                                           |
___________________________________________________________|""")
                continue

            except ValueError:
                self.term_cleaner()
                print("\nInvalid input.")
                continue


    #### DIRECTORY SEARCHER ####


    def song_searcher(self):
        self.term_cleaner()
        while True:
            is_stream = False
            countr = 0
            song_path_len = max(self.song_paths, default=0)+1

            
            """Folder printer"""
            # For every file in bnuuyplayer's folder, if dir print it
            # if theres no folders, break out
            print("""
___________________________________________________________
▼ Folders found in current dir ▼                           |
___________________________________________________________|
                                                           \\/""")
            
            for file in os.listdir(self.bnuy_path):

                file = os.path.join(self.bnuy_path, file)
                if os.path.isdir(file):
                    print(f"{file}")
                    countr += 1

            if countr == 0:
                self.term_cleaner()
                print("No folders found! please use one of the other methods.")
                break


            name = input("""___________________________________________________________\\/
Please enter the folder name you'd like to select          |
 __________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) return                                                  |
___________________________________________________________|

>>> """)

            if name == "0":
                break


            results = {}
            res_len = len(results)

            # Goes through and searches for directories in the current dir.
            try:
                for root, dirs, _ in os.walk(self.bnuy_path):
                    if name in dirs:
                        res_len += 1

                        combined = os.path.join(root, name)
                        results[res_len] = (name, combined, is_stream, self.audio_funct)


                # If multiple folders are found, print every root and key 
                # and ask the user for one of them, or all
                if len(results) > 1:
                    print("\nMultiple folders found!")

                    while True:
                        for key, (name, root, _, _) in results.items():
                            print(f"{key}) found at: {root}")
                        choice = int(input("""
___________________________________________________________
Which one is correct? If all are, enter "0"                |
___________________________________________________________|

>>> """))

                        if choice > len(results) or choice < 0:
                            print("Invalid option.")
                            continue
                        else:
                            break

                    # writes every found entry into playlists
                    if choice == 0:
                        for key, (name, root, _, _) in results.items():
                            song_path_len += 1
                            self.song_paths[song_path_len] = (name, root, is_stream, self.audio_funct)
                            combined = root

                    # write chosen one into playlists
                    else:
                        song_path_len += 1
                        name, root, _, _ = results[choice]
                        self.song_paths[song_path_len] = (name, root, is_stream, self.audio_funct)
                        combined = root

                # if only 1 is found, write immediately
                elif len(results) == 1:
                    song_path_len += 1
                    _, combined, _, _ = results[1]
                    self.song_paths[song_path_len] = results[1]

                else:
                    raise Escape

                self.term_cleaner()
                choice = int(input(f"""
__________________________________________________________/\\
Successfully found at {combined}!
__________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           | 
1) Add another folder                                      |
0) Return to BnuuyPlayer.                                  |
___________________________________________________________|

>>> """))
                self.saver()
                self.initializer()

                if choice == 0:
                    break
                elif choice == 1:
                    continue
                else:
                    self.term_cleaner()
                    raise ValueError

            except Escape:
                self.term_cleaner()
                print("\nFolder not found.")
                continue

            except ValueError:
                self.term_cleaner()
                print("\nInvalid input.")
                continue



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

    #### YOUTUBE DOWNLOADER/STREAMER ####


    def yt_adder(self):
        # Used to filter correct and false domains
        valid_domains = {"youtube.com",
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

        # Used to filter correct and false video extensions
        vid_ext = {"mp4",
                   "webm",
                   "mkv",
                   "avi",
                   "mov",
                   "dv",
                   "mpg",
                   "mpeg",
                   "m4v",
                   "ts",
                   "mxf",
                   "ogv",
                   "rm",
                   "swf",
                   "flv",
                   "gxf",
                   "asf",
                   "wmv",
                   "3gp",
                   "3g2",
                   "f4v",
                   "nuv",
                   "roq",
                   "ivf",
                  }

        while True:
            try:
                song_path_len = max(self.song_paths, default=0)+1
                choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Download the video/playlist(may take alot of storage)   |
2) Stream the video/playlist(Online only)                  |
0) Back                                                    |
___________________________________________________________|

>>> """))

                self.term_cleaner()

                url_inp = ":3"
                while True:

                    # if the choice ISNT 0; it runs this
                    if choice != 0:
                        try:

                            url_inp = input("""
___________________________________________________________
Enter a url                                                |
                                                           |
___________________________________________________________|         
▼ Extra commands ▼                                         |
                                                           |
0) Back/cancel                                             |
___________________________________________________________|

>>> """)
                            # returns to last menu
                            if url_inp == "0":
                                break
                            # filters through to find matching domain 
                            tmp_url = [url for url in valid_domains if url in url_inp]


                            # if no matches found, raise badurl
                            if len(tmp_url) == 0:
                                raise BadURL


                            url_valid = requests.get(url_inp, timeout=10)
                            # Checks url's validity
                            url_valid.raise_for_status()

                            """Invalid/wrong URL handler"""
                        except BadURL:
                            self.term_cleaner()
                            print("""Unsupported domain!\n 
___________________________________________________________ 
▼ Bnuuyplayer supports ▼                                  /\\""")
                            for domain in valid_domains:
                                print(domain)

                            print("__________________________________________________________\\/")
                        
                            """Internet error"""
                        except requests.exceptions.ConnectionError as e:
                            self.term_cleaner()
                            print(f"No internet, DNS error or refused connection, full error below. \n\n{e}")
                            continue

                            """General error"""
                        except(
                            requests.exceptions.MissingSchema,
                            requests.exceptions.InvalidSchema,
                            requests.exceptions.InvalidURL,
                            requests.exceptions.InvalidHeader,
                        ) as e:
                            self.term_cleaner()

                            print(f"Invalid URL, or an issue occurred regarding the URL occurred. Full error may be below  \n{e}")
                            continue

                            """Timeout"""
                        except requests.exceptions.Timeout:
                            self.term_cleaner()
                            print("Timeout error, URL took too long to respond.")

                            """HTTPError"""
                        except requests.exceptions.HTTPError as e:
                            self.term_cleaner()
                            print(f"An unknown error occurred, error message from the server ▼ \n\n{e}")


                        # if no error occurs, this runs as the url is likely valid 
                        # this breaks out of the inner loop to let the code continue
                        else:
                            break

                    elif choice == 0:
                        break

                    else:
                        print("Invalid input!")
                        continue

                if url_inp == "0":
                    self.term_cleaner()
                    continue

                elif choice == 1:
                    self.term_cleaner()
                    dl_location = int(input("""
___________________________________________________________
Where would you like to download the file(s)?              |
___________________________________________________________|
▼ Commands ▼                                               |
                                                           |
1) Put the song(s) in a existing local playlist.           |
2) Allow BnuuyPlayer to make a folder.                     |
0) Return.                                                 |
___________________________________________________________|

>>> """))
                    match dl_location:
                        case 1:

                            self.term_cleaner()
                            while True:
                                self.term_cleaner()

                                # prints every playlist and writes to tmp_dict

                                print_results = self.lib_print(local_only=True)

                                countr = print_results.get("local_countr")
                                local_dict = print_results.get("local_dict")
                                keys = print_results.get("display_keys")

                                # if no playlists this runs
                                if len(local_dict) < 1:
                                    print("\nNo playlists currently available.")
                                try:
                                    dl_dest = int(input("""
___________________________________________________________
Pick a playlist.                                           |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return. (Note: this return's behavior will be redone)   |
___________________________________________________________|

>>> """))
                                    # selects the playlist from tmp via dict unpacking
                                    if dl_dest != 0:
                                        (name, path, _, _) = local_dict[keys[dl_dest][0]]
                                        break

                                    elif dl_dest == 0:
                                        return

                                    else:
                                        self.term_cleaner()
                                        print("Invalid input!")
                                        continue

                                except KeyError:
                                    self.term_cleaner()
                                    print("Invalid input, bad number entered!")
                                    continue

                        case 2:
                            self.term_cleaner()

                            while True:
                                folder_name = input("""
___________________________________________________________
What would you like to name the folder?                    |
___________________________________________________________|

>>> """)
                                # combines bnuy path and folder name then creates
                                try:
                                    path = os.path.join(self.bnuy_path, folder_name)
                                    os.makedirs(path)
                                    break

                                except FileExistsError:
                                    self.term_cleaner()
                                    print("Folder already exists.\n")
                                    continue

                                except OSError as e:
                                    self.term_cleaner()
                                    print(f"OSError occurred! Error msg: {e}")
                                    continue

                            self.term_cleaner()
                            disp_name = input("""
___________________________________________________________
Would you like a display name for the folder?              |
                                                           |
1) No, continue.                                           |
0) Return                                                  |
___________________________________________________________|

>>> """)
                            # if user selects 0, use folder name
                            # else use disp name
                            name = None
                            if disp_name == "1": name = folder_name

                            elif disp_name == "0": 
                                self.term_cleaner()
                                continue

                            else: name = disp_name

                            is_stream = False
                            next_key = max(self.song_paths, default=0)+1
                            self.song_paths[next_key] = (
                                f"{name}",
                                path,
                                is_stream,
                                self.audio_funct,
                             )

                        # return to last menu
                        case 0:
                            continue

                        case _:
                            raise ValueError

                    self.term_cleaner()

                    while True:
                        ext = input("""
___________________________________________________________
Enter the file extension you'd like.                       |
___________________________________________________________|
▼ Recommended extensions ▼                                 |
                                                           |
mp3     (Audio)                                            |
m4a     (Audio)                                            |
m4v     (Video)                                            |
mp4     (Video)                                            |
___________________________________________________________|
▼ Unsupported extensions ▼                                 |
                                                           |
midi/mid                                                   |
mod, xm, s3m                                               |
wma                                                        |
___________________________________________________________|
▼ Extra commands         ▼                                 |
0) Return                                                  |
___________________________________________________________|

Warning: Do not include a dot when entering the file extension.

>>> """)

                        
                        yt_opts = {
                                "outtmpl": f"{path}/%(title)s.%(ext)s",
                                "format": "bestaudio/best",
                                "progress_hooks": [self.yt_hook],
                                "ignoreerrors": "only_download",
                                "no_warnings": True,
                                "postprocessors": [{
                                    "key":"FFmpegMetadata", "add_metadata": True,
                                    }]
                                }
                        yt_processor = {
                            "postprocessors": [{
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": ext,},
                                {
                                "key":"FFmpegMetadata", "add_metadata": True,
                                }],
                            }

                        if "." in ext:
                            print("Invalid ext, do not include a dot!")
                            continue

                        # deletes file sys folder to prevent orphaned folders
                        elif ext == "0":
                            if dl_location == 2:
                                os.rmdir(path)
                                del self.song_paths[next_key]

                            break

                        # if its a audio format; use postprocessors, else dont
                        elif ext not in vid_ext:
                            yt_opts.update(yt_processor)

                        else:
                            yt_opts["format"] = f"best[ext={ext}]"

                        self.term_cleaner()

                        # start downloading, yt opts for flags
                        try:
                            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                                ydl.download(url_inp)

                        except (yt_dlp.utils.DownloadError, yt_dlp.utils.PostProcessingError) as e:
                            if "unsupported" in str(e).lower():
                                print("Unsupported URL, or a invalid URL was inputted.")
                            else:
                                print(
                                f"Download failed, error message; {repr(e)}\n\nPlease report the error to the github page if its not a connection error."
                                )
                            continue

                        # if no errors occur, print this
                        print("\nSuccessfully downloaded!\n")

                        self.initializer()
                        self.saver()

                        break

                # stream path
                elif choice == 2:

                    if url_inp == "0":
                        break


                    name_choice = input("""
___________________________________________________________
Enter a name.                                              |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """)

                    if name_choice == "0":
                        break

                    is_stream = True

                    # writes to song paths
                    self.song_paths[song_path_len] = (
                        name_choice,
                        url_inp,
                        is_stream,
                        self.audio_funct,
                    )

                    self.saver()
                    print("Successfully added!")
                    self.initializer()

                elif choice == 0:
                    break

                else:
                    raise ValueError

            except (ValueError, KeyError):
                self.term_cleaner()
                print("\nInvalid input.")
                continue

    #### FOLDER METHODS ####

    def create_folder(self):
        while True:
            try:
                self.term_cleaner()
                folder_name = input("""
___________________________________________________________ 
Enter a name for the folder                                |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """)

                if folder_name == "0": break

                # This is used to identify folders 
                # This works as reg playlists always are a tuple in the 0 index 
                # while the 0 index in folders are a str to differentiate 
                folder_id = "Folder"
                tmp_list = []
                tmp_list.append(folder_id)
                tmp_list.append(folder_name)
                next_key = max(self.song_paths, default=0)+1
                self.song_paths[next_key] = tmp_list

                self.term_cleaner()

                while True:

                    self.saver()
                    choice = input("""Successfully created folder!\n 
___________________________________________________________ 
▼ Commands ▼                                               |
                                                           |
1) Create another folder                                   |
0) Return                                                  |
___________________________________________________________|

>>> """)

                    match choice:
                        case "1": break
                        case "0":  raise Escape
                        case _: 
                            print("Invalid input!")
                            continue

            except Escape:
                break

    #### Folder adder ####

    def folder_adder(self):
        while True:
            try:
                res = self.lib_print()
                folder_choice = input("""
___________________________________________________________\\/
Enter a playlist num then a folder num (e.g, 4 6)          |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
h) Help                                                    |
___________________________________________________________|

>>> """)
                self.term_cleaner()
                if folder_choice == "0": break
                elif folder_choice.lower() == "h":
                    print("""
▼ The valid structure is ▼
(playlist number) (folder number) 
separated by a space.

e.g) 4 6 
That will be the 4th playlist, and the folder associated with the number 6.""")
                    continue

                local = res.get("local_dict")
                stream = res.get("stream_dict")
                folders = res.get("folder_dict")
                display_keys = res.get("display_keys")

                # This is done to preserve the original keys, which full (in the passed dict) doesnt have.
                full = local | stream | folders

                keys = folder_choice.split()

                if len(keys) != 2:
                    print("Invalid input, please enter h for the help message.")
                    continue

                # Converts back into ints.
                int_keys = [int(key) for key in keys]

                playlist = full.get(display_keys[int_keys[0]][0])
                folder = full.get(display_keys[int_keys[1]][0])

                checked_keys = set()

                for key in folder[2:]:
                    checked_keys.add(key)

                if display_keys[int_keys[0]][0] in checked_keys:
                    print("Folder already has that playlist.")
                    continue


                err = None
                err_msg = {
                        "playlist_unfound": "No playlist found.",
                        "folder_unfound": "No folder found.",
                        "folder_is_playlist": "Selected folder was a playlist, invalid input",
                        "playlist_is_folder": "Selected playlist was a folder, invalid input",
                        "folder_is_liked_songs": "Can not add thentry into liked songs via this method.\nPlease go to playlist picker's song menu."
                        }

                if playlist is None: 
                    err = True
                    msg = err_msg.get("playlist_unfound")

                elif folder is None: 
                    err = True
                    msg = err_msg.get("folder_unfound")

                elif not self.folder_check(folder): 
                    err = True
                    msg = err_msg.get("folder_is_playlist")

                elif self.folder_check(playlist):
                    err = True
                    msg = err_msg.get("playlist_is_folder")
                
                elif folder[0] == "liked_songs":
                    err = True
                    msg = err_msg.get("folder_is_liked_songs")

                if err:
                    self.term_cleaner()
                    print(msg)
                    continue

                confirm = int(input(f"""
___________________________________________________________/\\
You will be adding {playlist[0]} (playlist/song)
into {folder[1]} (folder)
                                                           \\/
Is this correct?                                           |
___________________________________________________________|
1) Continue.                                               |
0) Return.                                                 |
___________________________________________________________|

>>> """))

                if confirm == 1: 
                    self.term_cleaner()

                    # This writes the key from self.song_paths rather then a copy
                    # appends it into the actual folder
                    folder.append(display_keys[int_keys[0]][0])
                    
                    # overwrites the old folder entry into the main library
                    self.song_paths[display_keys[int_keys[1]][0]] = folder
                    self.saver()

                    print("\nSuccess!\n")
                else:
                    self.term_cleaner()
                    continue
                

            except (ValueError, IndexError, KeyError):
                self.term_cleaner()
                print("Invalid input.")
                continue

    #### Folder del ####

    def folder_del(self):
        while True:
            try:
                res = self.lib_print(local_only=False, folder_only=True)
                folder_dict = res.get("folder_dict")
                keys = res.get("display_keys")

                del_choice = int(input("""
___________________________________________________________\\/
Which folder would you like to delete?                     |
___________________________________________________________|
0) Return                                                  |
___________________________________________________________|

>>> """))
                self.term_cleaner()
                if del_choice == 0: 
                    break

                match = folder_dict.get(keys[del_choice][0])

                if match is None:
                    self.term_cleaner()
                    print("Invalid input, no matches found.")
                    continue

                sentinel = match[0]

                if sentinel == "liked_songs":
                    self.term_cleaner()
                    print("Can not delete the liked songs folder.")
                    continue

                else: 
                    name = match[1]

                    confirm = int(input(f"""
__________________________________________________________/\\
You are deleting) {name}                                

Are you sure? this is permanent.                          \\/
___________________________________________________________|
1) Delete                                                  |
0) Return                                                  |
___________________________________________________________|

>>> """))

                    self.term_cleaner()

                    if confirm == 1:
                        self.internal_delete(keys[del_choice][0])
                        print("Successfully deleted.\n")
                        continue 
                    elif confirm == 0: 
                        print("Canceled.\n")
                        continue
                    else:
                        raise ValueError

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input.")
                continue

    #### LIKED SONG REMOVE ####.

    def liked_remover(self, folder):
        while True:
            songs = {}
            no_songs = False
            try:
                print("___________________________________________________________/\\")

                for path in folder[2:]:
                    songs[len(songs)+1] = path
                    print(f"{len(songs)}) {os.path.basename(os.path.splitext(path)[0])}")
                if len(songs) == 0: 
                    print("No liked songs found.")
                    no_songs = True
                choice = int(input("""
___________________________________________________________\\/
Select the song you want to unlike.                        |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                self.term_cleaner()

                if choice == 0: break 
                else:
                    if choice not in range(1, len(songs)+1) or no_songs:
                        print("Invalid input, no song at that number was found.")
                        continue

                    selected_path = songs[choice]

                    # This does a manual search because liked songs have no keys
                    for path in folder[2:]:
                        if path == selected_path:
                            folder.remove(selected_path)

                            self.term_cleaner()
                            print(f"Successfully unliked {os.path.basename(os.path.splitext(path)[0])}")
                            self.saver()
                            break
                    continue

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input!")
                continue


    #### PLAYLIST FROM FOLDER DEL ####

    def del_from_playlist(self):
        while True:
            try:
                res = self.lib_print(local_only=False, folder_only=True)

                folder_dict = res.get("folder_dict")
                library = res.get("full_dict")
                keys = res.get("display_keys")

                folder_choice = int(input("""
___________________________________________________________\\/
Please select a folder.                                    |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                if folder_choice == 0: break
                else:
                    folder = library[keys[folder_choice][0]]
                    if not self.folder_check(folder):
                        raise ValueError

                    if folder[0] == "liked_songs": 
                        self.liked_remover(folder)
                        continue

                    res = self.folder_manager(folder)
                    if res is not None:
                        del_playlist = res.get("selected")
                        key = res.get("key")

                    else: del_playlist = None

                    # Backing out to callerroute
                    if del_playlist is None: return

                    self.term_cleaner()
                    confirm = int(input(f"""
__________________________________________________________/\\
You will be deleting {del_playlist[0]} inside {folder[1]}
                                                          \\/   
Are you sure? this will move the playlist out.             |
___________________________________________________________|
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|

>>> """))

                    if confirm == 1:
                        folder.remove(key)
                        self.saver()
                        print("Success!\n")

                    elif confirm == 0: break

                    else: raise ValueError

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input")
                continue

    #### EDIT INTERNAL FOLDER NAME ####

    def edit_folder(self):
        self.term_cleaner()
        while True:
            try:
                res = self.lib_print(local_only=False, folder_only=True)
                folders = res.get("folder_dict")
                keys = res.get("display_keys")

                edit_choice = int(input(f"""
___________________________________________________________\\/
Please select a folder to rename.                          |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                if edit_choice == 0: break 

                selected = folders.get(keys[edit_choice][0])

                if selected is None:
                    self.term_cleaner()
                    print("Not a valid folder.")
                    continue

                else:
                    selected = folders.get(keys[edit_choice][0])
                    name = selected[1]
                    self.term_cleaner()
                    rename = input(f"""
_________________________________________________________/\\
Current name) {name}
Enter a new name below                                   \\/
                                                          |
0) Return                                                 |
__________________________________________________________|

>>> """)

                    if rename == "0": break 
                    else: 
                        print("Success!")
                        selected[1] = rename
                        self.song_paths[keys[edit_choice][0]] = selected
                        self.saver()


            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input.")
                continue
    
    #### DELETE PLAYLIST ####

    def del_playlist(self):
        while True:
            try:
                self.term_cleaner()
                print("___________________________________________________________/\\")
                res = self.lib_print()
                keys = res.get("display_keys")

                del_choice = int(input("""
___________________________________________________________ 
                                                           \\/
Which would you like to delete?                            |
(This only deletes the playlist from BnuuyPlayer!)         |
___________________________________________________________|
▼ Extra commands ▼                                         |
0) return                                                  |
___________________________________________________________|

>>>"""))

                if del_choice == 0: return

                else:
                    self.term_cleaner()

                    playlist = self.song_paths[keys[del_choice][0]]

                    if self.folder_check(playlist):
                        self.term_cleaner()
                        print("Can not delete folders here, please select a playlist!")
                        continue

                    confirm = int(input(f"""Are you sure?
You are deleting {playlist[0]}

1) Confirm
0) Return

>>> """))

                    if confirm == 1:
                        self.internal_delete(keys[del_choice][0])
                    elif confirm == 0: continue
                    else: raise ValueError

                    print("Successfully deleted!")
                    continue

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input!")
                continue

    #### DELETE PLAYLIST FROM DISK ####

    def del_playlist_from_disk(self):
        while True:
            try:

                self.term_cleaner()

                results = self.lib_print(local_only=True)
                # assigns values
                local_paths = results.get("local_dict")
                countr = results.get("local_countr")
                keys = results.get("display_keys")
                # lib print sets local back to False as a side effect

                del_choice = int(input("""___________________________________________________________\\/
Which playlist would you like to delete?                   |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                if del_choice == 0: return

                """Delete processer"""
                # find the path, remember name for later
                delname, path, _, _ = local_paths[keys[del_choice][0]]
                while True:
                    final_confirm = input(f"""
___________________________________________________________/\\
Are you sure? you are deleting) {delname}
This is permanent.                                         \\/
                                                           | 
1) Delete                                                  |
0) Return                                                  |
___________________________________________________________| 

>>> """)

                    if final_confirm == "0": 
                        self.term_cleaner()
                        print("Canceled.")
                        break

                    elif final_confirm == "1":

                        """Recursive delete"""
                        shutil.rmtree(path)

                        """Library updater"""
                        # Reindexes and deletes selected playlist
                        self.internal_delete(keys[del_choice][0])
                        print("Successfully deleted!")
                        break

                    else:
                        self.term_cleaner()
                        print("Invalid input!")
                        continue

            except ValueError:
                self.term_cleaner()
                print("Invalid input!")
                continue

            except KeyError:
                self.term_cleaner()
                print("Invalid input, only playlists are selectable!\n")
                continue

    #### ADD PLAYLIST ####
    
    def add_playlist(self):
        while True:
            try:
                choice = self.adder_menu()

                if choice == 0: return # Return to last menu

                funct = self.adders[choice]()
                break

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input!")
                continue

    #### EDIT PLAYLIST NAME ####

    def edit_playlist_name(self):
        while True:
            try:
                results = self.lib_print(local_only=True)
                countr = results.get("full_countr")
                local_paths = results.get("full_dict")
                keys = results.get("display_keys")

                self.term_cleaner()
                rename_choice = int(input("""
___________________________________________________________\\/
Which playlist would you like to rename?                   |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))
                if rename_choice == 0: return

                if countr > 0 and rename_choice in range(1,len(keys)+1):
                    selected_key = keys[rename_choice][0]

                    playlist = self.song_paths[selected_key]

                    if self.folder_check(playlist):
                        self.term_cleaner()
                        print("Can not rename folders here!")
                        continue

                    self.term_cleaner()
                    new_name = input(f"""
___________________________________________________________/\\
You will be renaming) {playlist[0]}
Please enter a new name.                                   \\/
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """)

                    if new_name == "0": continue 

                    if new_name == "liked_songs":
                        self.term_cleaner()
                        print(f"Failure) {new_name} is a reserved name for BnuuyPlayer :(")
                        print("You can name the playlit a variation of it instead :3")
                        continue

                    playlist = list(playlist)
                    playlist[0] = new_name
                    self.song_paths[selected_key] = tuple(playlist)
                    self.saver()
                    self.term_cleaner()

                    print("Successfully renamed. :3")
                    continue

                else: raise ValueError
                                    

            except ValueError:
                self.term_cleaner()
                print("Invalid input")
                continue
        
    #### INTERNAL PLAYLIST EDITOR ####

    def internal_delete(self, num):
        for key, tupl in self.song_paths.items():
            # Folders are lists; therefore we can use .remove()
            if self.folder_check(tupl) and num in tupl:
                tupl.remove(num)

        del self.song_paths[num]

        self.saver()


    #### METADATA PRINT AND COLLECTION ####
    def metadata_helper(self, path):
        count = 0
        metadata = {}

        invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".wma", ".lrc", ".py"}
        unsupported_ext = {".webm", ".mkv", ".it", ".avi", ".mov", "mpg", ".mpeg", ".ts", ".flv", ".3gp"}

        for file in os.listdir(path):
            abs_path = os.path.join(path, file)

            key = max(metadata, default=0)+1

            if os.path.splitext(os.path.basename(file))[1] in invalid_ext:
                continue
            elif os.path.splitext(os.path.basename(file))[1] in unsupported_ext:
                continue

            metadata[key] = mutagen.File(abs_path, easy=True)
            print(f"{key}) {os.path.basename(file)}")

        print("\nNote: if a song is missing, the file format is likely unsupported.")

        return metadata


    #### WRITE SONG METADATA ####

    def metadata_handler(self, playlist, mode):
        self.term_cleaner()
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
                    self.term_cleaner()
                    print("No songs in this playlist! :(")

                print("""___________________________________________________________\\/
▼ Valid tags ▼                                             /\\
""")
                for tag in tags.keys(): print(tag)


                write_select = input(f"""___________________________________________________________\\/
{enter_msg}
e.g) 3 album                                               _
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """)

                values = write_select.split()

                if write_select == "0": 
                    self.term_cleaner()
                    return

                elif len(values) != 2: raise ValueError

                elif int(values[0]) not in range(1, len(metadata)+1):
                    self.term_cleaner()
                    print(f"Invalid input, select a song from 1-{len(metadata)}")
                    continue

                else: 
                    num, tag = values

                selected_tag = tags.get(tag)

                if selected_tag is None:
                    self.term_cleaner()
                    print("Invalid tag, please enter a valid one.")
                    continue


                self.term_cleaner()
                data = metadata.get(int(num))

                true = True
                retry = False
                try: 
                    curr_tag = data[f"{tag}"]
                except KeyError:
                    # KeyError occurs when no metadata exists
                    curr_tag = "No data available :("


                while true:

                    new_data = input(f"""
__________________________________________________________/\\
{data_choice}
Selected tag) {tag}
Current tag data) {curr_tag}
                                                          \\/
0) Return                                                  |
___________________________________________________________|

>>> """)

                    if new_data == "0": 
                        true = False
                        retry = True
                        break
                    else: break

                self.term_cleaner()
                if retry: continue 

                if curr_tag != "No data available :(": old_data = data[f"{tag}"]

                else: old_data = "No data :("

                if mode == "add":
                    data[f"{tag}"] = new_data
                else:
                    try:
                        data.pop(f"{tag}")
                    except KeyError:
                        self.term_cleaner()
                        print("This key doesnt exist!")
                        continue
                data.save()
                if mode == "add":
                    print(f"Successfully changed {old_data} to {new_data}!")
                else:
                    print(f"Successfully deleted {old_data}!")


            except ValueError:
                self.term_cleaner()
                print("Invalid input!")
                continue

    #### METADATA SUBSETTINGS ####

    def metadata_settings(self):
        self.term_cleaner()
        metadata_methods = {
                "add": self.metadata_handler,
                "del": self.metadata_handler,
                }

        while True:
            try:
                res = self.lib_print(local_only=True)
                keys = res.get("display_keys")

                selection = input("""
__________________________________________________________\\/
▼ Metadata settings ▼                                      |
                                                           |
add) Add new metadata.                                     |
del) Delete metadata.                                      |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|
Input: <playlist num> <setting>

>>> """)

                selected_stuff = selection.split()

                if selection == "0":
                    self.term_cleaner()
                    return

                if len(selected_stuff) != 2:
                    print("Please select the playlist, then what setting you'd like in the same message.")
                    print("Seperated by a space.")
                    continue
                
                num = int(selected_stuff[0])
                cmd = selected_stuff[1]

                playlist = self.song_paths[keys[num][0]]
                if self.folder_check(playlist):
                    self.term_cleaner()
                    print("Please select a playlist and not a folder!")
                    continue
                metadata_methods[cmd](playlist, cmd)


            except (KeyError, ValueError):
                self.term_cleaner()
                print("Invalid input! select a playlist then the command.")
                continue

    #### PLAYLIST SETTINGS #### 
    def playlist_settings(self):
        settings = {
                #### FOLDER METHKDS ####
                1: self.create_folder,
                2: self.folder_adder,
                3: self.folder_del,
                4: self.del_from_playlist,
                5: self.edit_folder,

                #### PLAYLIST METHODS ####
                6: self.del_playlist,
                7: self.del_playlist_from_disk,
                8: self.add_playlist,
                9: self.edit_playlist_name,
                }
        while True:
            try:
                choice = int(input("""
___________________________________________________________ 
▼ BnuuyFolder settings ▼                                   |
(Note: These are not File system folders)                  |
                                                           |
1) Create a folder                                         |
2) Copy playlist into a folder                             |
3) Delete a folder                                         |
4) Remove a playlist from a folder                         |
5) Edit a folder name                                      |
___________________________________________________________| 
▼ Playlist settings ▼                                      |
                                                           |
6) Delete a playlist from BnuuyPlayer                      |
7) Delete a playlist from disk                             |
8) Add a playlist/song                                     |
9) Edit a playlist name                                    |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Back                                                    |
___________________________________________________________|

>>> """))

                self.term_cleaner()

                ####rExtra commands ####
                if choice == 0: 
                    """Back"""
                    break

                elif choice in range(1, len(settings)+1):
                    settings[choice]()
                    continue

                else: raise ValueError 

            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input!")
                continue

    #### SETTINGS / NON-MUSIC ####
    def settings(self):
        while True:
            try:

                choice = int(input(f"""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Toggle shuffle. (Currently: {self.shuffl[1]}                |
2) BnuuyFolder/Playlist sub settings                       |
3) Song Metadata settings                                  |
0) Return.                                                 |
___________________________________________________________|

>>> """))
                self.term_cleaner()

                if choice == 0:
                    self.saver()
                    break

                elif choice == 1:
                    """Shuffle toggler"""
                    # toggles shuffle's true/false
                    self.shuffl[0] = not self.shuffl[0]

                    if self.shuffl[0]:
                        self.shuffl[1] = "activated)  "
                    else:
                        self.shuffl[1] = "deactivated)"

                    self.term_cleaner()

                elif choice == 2:
                    """Playlist sub settings"""
                    self.playlist_settings()

                elif choice == 3:
                    """Metadata settings"""
                    self.metadata_settings()


                else:
                    raise KeyError
            except (ValueError, KeyError):
                self.term_cleaner()
                print("Invalid input.\n")


    #### INITIAL SETUP ####


    def file_setup(self):

        self.term_cleaner()
        if not self.initialized:
            while True:
                try:
                    print("""
⠀⠀⠀⡤⣤⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⡶⠶⡶⣤⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣸⠉⠉⠙⠶⣶⣄⠀⠀⠀⠀⠀⠀⣾⠉⣀⣀⠉⠻⠶⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⣿⠀⡖⢶⣀⡉⠉⣷⠀⠀⠀⠀⠀⣿⠀⡇⠉⢶⣄⠤⣿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⡀⠀⠀⠀⠀⠀
⠀⠀⣿⣀⢇⠈⠋⣷⠉⠉⣿⠀⠀⠀⠀⣿⠀⡇⠀⠀⢿⣀⡷⠿⣀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣿⠿⠽⠉⠉⠉⠭⠿⣿⣿⣀⠀⠀⠀
⠀⠀⠀⣿⠀⡇⠈⠙⣷⠠⠿⣀⡀⠀⠀⣿⠀⡇⠀⠀⠀⣿⡇⢀⣿⠃⠀⠀⠀⠀⢀⣀⣾⢿⠀⠀⠀⠀⠀⠀⠀⠀⠉⠉⠿⣷⣀⡀
⠀⠀⠀⠉⣾⠛⡀⠀⣿⠀⢘⣿⡇⠀⠀⠿⢀⠉⡂⠀⠀⣿⡆⢸⣿⣷⠶⠶⠶⠶⠿⠿⣿⣤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⡇
⠀⠀⠀⠀⠙⣷⠉⢶⣿⣶⠻⣿⣇⣀⣀⣬⣶⡆⠀⠀⣶⣿⡅⣙⣿⠋⠀⠀⠀⠀⠀⠀⠉⠙⣷⣶⣤⡄⠀⠀⠀⠀⠀⠀⠀⠀⣿⣶
⠀⠀⠀⠀⠀⢩⣶⣿⣿⠿⠶⠉⠁⠉⠯⣿⣿⠇⣄⣶⣿⢿⢷⣿⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠇⠉⠯⣷⣆⣐⠀⠀⠀⠀⠀⠀⠩⣿
⠀⠀⠀⠀⢀⣘⠿⠍⠉⠀⠀⠀⠀⠀⠀⠉⠿⠆⣿⣿⣿⠮⣿⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠧⠀⠉⢿⣿⣀⠀⠀⠀⠀⠀⣸⣿
⠀⠀⠀⠀⣟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠯⡉⠀⠉⠸⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠿⣿⠶⣀⠀⠀⣀⣿⡏
⠀⠀⠀⣶⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠁⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⣷⣿⡿⠉⠁
⠀⠀⣾⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⡿⠋⠀⠀⠀
⠀⠀⣿⡷⢶⣄⠀⠀⠀⠀⢀⣠⡶⠶⠶⠶⢀⠀⠀⠀⠀⠀⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡏⠀⠀⠀⠀⠀
⠀⠀⣿⠱⣀⠉⣀⣀⣀⡀⠀⠉⠃⠀⠀⠀⠉⣀⣀⣖⡷⠶⠷⠄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⠀
⣰⠾⠿⣄⠈⠉⠗⠿⠟⠃⠀⠀⠀⠀⠀⠒⣒⡿⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⡇⠀⠀⠀⠀⠀
⣿⠀⠀⠉⠷⣤⣤⣀⠀⠀⠀⠀⠀⠀⣠⣤⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠀⠀⠀⠀⠀⠀⣄⣀⣾⣿⠉⠁⠀⠀⠀⠀⠀
⠿⠷⠶⠶⠶⠿⠶⠿⠿⠶⠶⠶⠾⠾⠿⠿⠿⠷⠾⠶⠷⠶⠾⠾⠾⠷⠷⠶⠾⠷⠾⠷⠶⠶⠾⠷⠾⠿⠿⠿⠋⠀⠀⠀⠀⠀⠀⠀
 ________________________________________________________________________
|Welcome to BnuuyPlayer!                                                 |
|________________________________________________________________________|

To use BnuuyPlayer, there must first be a valid song folder/playlist.""")
                    choice = self.adder_menu()
                    self.term_cleaner()

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
                    self.term_cleaner()
                    print("\nInvalid Input.")
                    continue


    #### MAIN MENU ####


    def main_menu(self):

        self.saver()
        print("""
              ⠀⠀⣠⡶⢶⣦⠀⠀⠀⣠⡶⢶⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
              ⠀⢰⡟⠀⠀⢹⣧⠀⣸⠏⠀⠀⢻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
              ⠀⣿⠁⠀⠀⠀⢿⣴⡿⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
              ⠀⣿⠀⠀⠀⠀⢸⣿⠇⠀⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
              ⠀⢿⡆⠀⠀⠀⠈⣿⠀⠀⠀⠀⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⡀⠀⠀⠀⠀⠀
              ⠀⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⢰⣟⠀⠀⠀⣀⣀⣀⣀⣀⣾⠋⠉⠹⣇⠀⠀⠀⠀
              ⠀⣰⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣧⣶⠞⠋⠉⠀⠈⠉⠃⠀⠀⢠⡟⠀⠀⠀⠀
              ⢠⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠻⣦⡀⠀⠀
              ⣸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢘⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢷⣄⠀
              ⢿⡇⠸⣿⠀⠀⠀⠀⠀⠀⣴⣆⠀⢸⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡆
              ⠸⣧⡀⠀⠀⢀⣶⣶⡆⠀⠈⠁⣰⡟⠁⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⣸⡇
              ⠀⠙⠻⣦⣄⣀⣀⣈⣁⣀⣤⠾⠋⠀⠀⠀⠀⠀⣀⣠⣴⡶⢿⡿⠿⠶⣶⠶⠟⠀
              ⠀⠀⢠⡟⠉⢙⣿⠛⠋⠉⠁⠀⠀⣀⣠⣴⠶⠟⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
              ⠀⠀⠘⢿⣤⣘⣿⡀⠀⠀⢀⣴⡿⠋⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
              ⠀⠀⠀⠀⠈⠉⠙⠛⠻⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
___________________________________________________________
Welcome back to BnuuyPlayer!                               |
___________________________________________________________|\n""")

        while True:
            """Menu printer"""
            # Iterates through main operations and prints
            try:
                print("""___________________________________________________________
                                                          /\\""")
                for key, (name, _, _) in self.main_operations.items():
                    print(f"{key}) {name}")
                print("__________________________________________________________\\/")
                if not self.no_hint:
                    print("""▼ Extra commands ▼                                         |
                                                           | 
h/H) Extra information, use if you're lost.                |
t) Toggle this message off/on.                             |
___________________________________________________________|""")
                choice = input(">>> ").lower()

                """Help menu printer"""
                # Takes the hint section from the dict with name and num
                # then prints them together in a for loop
                if choice == "h":
                    self.term_cleaner()
                    print("""
___________________________________________________________
                                                          /\\""")
                    for num, (name, hint, _) in self.main_operations.items():
                        print(f"{num}) {name} \n Info: {hint}")

                    print("___________________________________________________________\\/\n")
                    continue

                elif choice.lower() == "t":
                    self.term_cleaner()

                    # Toggles no hint off/on
                    self.no_hint = not self.no_hint

                    # writes to disk
                    self.saver()
                    print("Successfully toggled.\n")
                    continue

                self.term_cleaner()
                name, _, function = self.main_operations[choice]
                if name == "Exit":
                    self.saver()

                # Framework for future lrc prettifier
                if choice == "1":
                    audio_thrd = threading.Thread(target=self.audio_funct, daemon=True)
                    audio_thrd.start()
                    audio_thrd.join()

                else: function()

            except KeyError:
                self.term_cleaner()
                print("\nInvalid input.")
                continue

    #### BNUUYSTART ####
    # Starts the main code loop
    def start_code(self):
        while True:
            if not self.initialized:
                self.file_setup()
            else:
                self.main_menu()

bnuystart = BnuuyPlayer(mutagen_installed)
