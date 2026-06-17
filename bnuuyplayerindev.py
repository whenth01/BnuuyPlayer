import os
import subprocess
import sys
import json
import threading
import time
import traceback
from shutil import rmtree
from shutil import which
from shutil import move

def err_dl(name):
    while True:

        try:
            confirm = input(f"""
A dependency({name}) failed to import.
Would you like to download it?

1) Download 
0) Exit 

>>> """)

            if confirm == "1":
                # Equivalent to writing pip install {name} in the terminal
                subprocess.check_call([sys.executable, "-m", "pip", "install", name])
                break
            elif confirm == "0": sys.exit()

            else: 
                print("Invalid input.\n")
                continue

        except(KeyboardInterrupt, OSError) as e:
            print("An error occurred!")
            print(f"▼ Error message ▼ \n\n{e}")
            sys.exit()

try: import requests
except (ModuleNotFoundError, ImportError):
    err_dl("requests")
    import requests

try: import yt_dlp
except (ModuleNotFoundError, ImportError):
    err_dl("yt-dlp")
    import yt_dlp

# Checks if MPV is installed
check = which("mpv")

if check is None:
    print("MPV is not installed. Please install the MPV package.")
    sys.exit()

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

    def __init__(self):

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
               "folder_manager",
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
    # Currently unimplemented, this will run on startup in a separate thread 
    # to show the user a stat on how long they've been using BnuuyPlayer.
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
                raise FileNotFoundError

        except FileNotFoundError:
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
                        time_elapsed = time.strftime("%H:%M:%S", time.gmtime(self.time_used))
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
            elif player == (0, 0): return
            else: break

        print("")

        try:
            # lrc_thrd = threading.Thread(target=lrc_funct, daemon=True)
            # lrc_thrd.start()
            self.binding_menu()
            subprocess.run(player, check=True)
            self.term_cleaner()

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

        if tupl[0] in self.valid_sentinels: return True
        else: return False
    
    #### DEFAULT FOLDER CREATOR ####

    # Creates a default internal folder if they dont exist
    def default_folders(self):
        liked_exists = False
        manager_exists = False

        for num, tupl in self.song_paths.items():
            if tupl[0] == "liked_songs":
                liked_exists = True

            elif tupl[0] == "folder_manager":
                manager_exists = True

        if liked_exists is not True:
            self.song_paths[len(self.song_paths)+1] = ["liked_songs", "Liked songs",]

        if manager_exists is not True:
            self.song_paths[len(self.song_paths)+1] = ["folder_manager", "Playlist manager",]


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

        folder_comp = {}

        for _, tupl in folder_dict.items():
            conv = list(tupl)
            keys = set(conv[2:])
            folder_comp[len(folder_comp)+1] = keys

        if len(folder_comp) != 0:
            folder_comp = set.union(*folder_comp.values())

        # We dont neee to reenumerate here as it was already done earlier.
        full_dict = tmp_full_dict | folder_dict

        self.song_paths = full_dict

        #### DISPLAY DICT ####
        # This compiles the keys from self.song_paths into a clean architecture.
        display_keys = {}
        folder_cache = {}

        for key, tupl in self.song_paths.items():

            # I used this method to keep them temporarily seperate.
            if self.folder_check(tupl): 
                folder_cache[len(folder_cache)+1] = (key, True)
            else:
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
        print("▼ Folders ▼                                                /\\\n")

        disp_num = None
        for disp_num, (og_key, is_folder) in display_keys.items():
            tupl = self.song_paths[og_key]

            if is_folder:
                print(f"{disp_num}) {tupl[1]} ({tupl[0]})")

        if disp_num is None:
            print("No folders found.")

        print_results = {
            "full_dict": full_dict,
            "stream_dict": stream_dict,
            "local_dict": local_dict,
            "folder_dict": folder_dict,

            "full_countr": full_countr,
            "stream_countr": stream_countr,
            "local_countr": local_countr,
            }

        return print_results

    def liked_manager(self, tupl):
        songs = {}

        print("""
___________________________________________________________/\\
▼ Liked songs ▼""")

        for path in tupl[2:]:
            if not os.path.isfile(path):
                found = False
                """Song search"""
                for root, dirs, files in os.walk(self.bnuy_path):

                    for file in files:
                        if os.path.basename(path) == file:
                            path = os.path.join(root, file)
                            found = True

                            break 

                    if found: 
                        songs[len(songs)+1] = path
                        break

                if found is False: 
                    print("A liked song disappeared; was it deleted or moved out?")
                    print(f"Missing song) {os.path.basename(os.path.splitext(path)[0])}")
                    continue

            else: songs[len(songs)+1] = path
                    
        return songs
        

    #### FOLDER MANAGER ####

    def folder_manager(self, tupl):
        disp_keys = {}
        while True:
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

                for key, (og_key) in disp_keys.items():
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
                if choice == 0:
                    break

                else:
                    return self.song_paths[choice]


            # temp debug code
            except ValueError:
                self.term_cleaner()
                print("Invalid input. \n")
                continue

    #### FILE.MOVER ####
    def move_file(self, path):
        while True:
            try:
                res = self.lib_print(local_only=True)

                library = res.get("full_dict")

                selection = int(input("""
___________________________________________________________\\/
Please select the location you'd like to move the song to. |
                                                           |
0) Return.                                                 |
___________________________________________________________|

>>> """))

                _, dest_path, _, _ = library[selection]
                confirm = int(input(f"""
___________________________________________________________ 
Are you sure?                                              /\\
Source) {path}
Destinaton) {dest_path}
___________________________________________________________\\/
▼ Commands ▼                                               |
                                                           |
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|

>>> """))
                if confirm == 1:
                    lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
                    for root, dirs, files in os.walk(path):
                        if lrc_file in files:
                            move(lrc_file, dest_path)
                            break
                    move(path, dest_path)
                    print("Successfully moved file!")

            except:
                traceback.print_exc()

    #### CMD HANDLER ####

    def cmd_handler(self, num, cmd, path):
        match cmd:

            case "l":
                """Like a song"""
                for _, tupl in self.song_paths.items():
                    if self.folder_check(tupl) and tupl[0] == "liked_songs":
                        tupl.append(path)
                        self.saver()
                        print("Successfully liked song!")
                        break
            case "d":
                """Delete song"""
                check = os.path.isfile(path)

                if check is False: 
                    print("Cannot delete streamed songs from disk.")
                    return
                else:
                    os.remove(path)
                    # This deletes the .lrc file.
                    lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
                    for root, dirs, files in os.walk(os.path.dirname(path)):
                        if lrc_file in files:
                            os.remove(lrc_file)
                            print(f"Successfully deleted) {lrc_file}")
                            break

                    print(f"Successfully deleted) {os.path.basename(path)}")

            case "m":
                """Move song"""
                self.move_file(path)

            case "c":
                """Copy song"""
                print("unimplemented")

            case "p":
                """Play song"""
                print("unimplemented")

            case _:
                print("Invalid input.")
                return


    #### PLAYLIST PICKER ####

    def playlist_picker(self):
        while True:

            try:

                countr = 0

                self.lib_print(local_only=False)

                choice = int(input("""__________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           |
0) back                                                    |
___________________________________________________________|

>>> """))

                self.term_cleaner()
                # defines values that local song picker requires
                countr = 0
                tmp_song = {}

                # causes audio funct to raise ValueError, causing a return to main menu
                if choice == 0:
                    self.term_cleaner()
                    return choice, countr

                
                tupl = self.song_paths[choice]
                liked_handler = False

                if self.folder_check(tupl):
                    values = self.folder_manager(tupl)
                    # return route
                    if values is None or len(values) == 0: continue 
                    # liked song route
                    if os.path.isfile(values[1]): 
                        liked_handler = True
                        path = values
                    # regular route
                    else: name, path, is_stream, function = values

                else: name, path, is_stream, function = tupl


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
                    for num, song in values.items():
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

                # Checks if the song path dict is empty, otherwise act normal

                if len(tmp_song) < 1:
                    self.term_cleaner()
                    print("Playlist is empty.\n")
                    continue

                choice = input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Play the whole playlist                                 |
2) Play one song(phase out soon)                           |
0) Back                                                    |
___________________________________________________________|
▼ Eztra commands ▼                                         |
                                                           |
(num) l — Like a song. Gets added to liked songs folder.   |
(num) d — Delete a song from disk.                         |
(num) m — Move a song to a new playlist.                   |
(num) c — Copy a song to a new playlist.                   | 
(num) p — Play a single song.                              |
___________________________________________________________|

>>> """)

                tmp_choice = choice.split()

                if len(tmp_choice) == 2:
                    num = int(tmp_choice[0])
                    cmd = tmp_choice[1]
                    path = tmp_song[num]

                    self.cmd_handler(num, cmd, path)
                    continue
                else: choice = int(choice)

                if choice == 1:
                    self.term_cleaner()
                    # automatically moves on, no need for extra logic


                elif choice == 2:
                    choice = int(input("""
___________________________________________________________
Enter the num of the song you'd like                       |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Back                                                    |
___________________________________________________________|

>>> """))
                    if choice == 0:
                        return None
                    path = tmp_song[choice]
                    liked_handler = False

                # Raises escape to enter outer loop and to return.
                elif choice == 0: break

                else:
                    raise ValueError

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
                traceback.print_exc()
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
                    return

                if "3" in failed: 
                    """Shuffl check"""
                    make_list = True

                if "4" in failed: 
                    """Time used check"""
                    print("Your time stat was corrupted/unrecoverable, setting to 0.")
                    self.time_used = 0

                solved = []
                for key, method in failed.items():
                    while True:
                        if key == "1" or key == "2" or key == "3":
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

        """Deleted folders scrubber"""
        # Deletes invalid/corrupted song paths.
        # separate from the other recoverer
        # activates only if del collection has more than 1 value
        if len(del_dict) >= 1:
            for num in del_dict:
                del self.song_paths[num]
            del_dict.clear()  

        """Reindexes song path keys"""
        # writes into main song paths after processing
        res = {i: v for i, v in enumerate(self.song_paths.values(), start=1)}
        self.song_paths.clear()
        self.song_paths.update(res)

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
                    self.song_paths[len(self.song_paths)+1] = (playlist_name, path_input, is_stream, self.audio_funct)

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
                print("Invalid input.\n")
                continue


    #### ADD/CREATE FOLDER ####


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

                    self.song_paths[len(self.song_paths) + 1] = (folder_name, song_path, is_stream, self.audio_funct)
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
                print("\nFolder or file already exists.")
                continue

            except OSError:
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
                print("\nInvalid input.")
                continue


    #### DIRECTORY SEARCHER ####


    def song_searcher(self):
        self.term_cleaner()
        while True:
            is_stream = False
            countr = 0
            song_path_len = len(self.song_paths)

            
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

                        if choice > key or choice < 0:
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
                print("\nFolder not found.")
                continue
            except ValueError:
                print("\nInvalid input.")
                continue



    #### YT Hook ####

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


            try:
                """lrclib lookup"""
                lrc_get = requests.get(f"https://lrclib.net/api/get?artist_name={artist}&track_name={title}&album_name={album}&duration={duration}", timeout=10)

            except(requests.exceptions.Timeout):
                print("\nTimeout!")
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


                with open(lrc_path, "w") as f:
                    f.write(lyric)
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
                song_path_len = len(self.song_paths) + 1
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

                if choice == 1:
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

                            # prints every playlist and writes to tmp_dict

                            print_results = self.lib_print(local_only=True)

                            countr = print_results.get("local_countr")
                            local_dict = print_results.get("local_dict")

                            # if no playlists this runs
                            if len(local_dict) < 1:
                                print("\nNo playlists currently available.")

                            dl_dest = int(input("""
___________________________________________________________
Pick a playlist.                                           |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return.                                                 |
___________________________________________________________|

>>> """))
                            # selects the playlist from tmp via dict unpacking
                            if dl_dest != 0:
                                (name, path, _, _) = local_dict[dl_dest]

                            else:
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
0) No, continue.                                           |
___________________________________________________________|

>>> """)
                            # if user selects 0, use folder name
                            # else use disp name
                            name = None
                            if disp_name == "0": name = folder_name
                            else: name = disp_name

                            is_stream = False
                            self.song_paths[len(self.song_paths) + 1] = (
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
mp3(Audio)                                                 |
m4a(Audio)                                                 |
m4v(Video)                                                 |
mp4(Video)                                                 |
webm(Video)                                                |
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
                                "ignoreerrors": True,
                                "no_warnings": True,
                                }
                        yt_processor = {
                            "postprocessors": [{
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": ext,}],
                            }

                        if "." in ext:
                            print("Invalid ext, do not include a dot!")
                            continue

                        # deletes folder to prevent orphaned folders
                        elif ext == "0":
                            if dl_location == 2:
                                os.rmdir(path)
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

                        except yt_dlp.utils.DownloadError as e:
                            if "unsupported" in str(e).lower():
                                print("Unsupported URL, or a invalid URL was inputted.")
                            else:
                                print(
                                f"Download failed, error message; {repr(e)}\n\nPlease report the error."
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

                self.song_paths[len(self.song_paths)+1] = tmp_list

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
seperated by a space.

e.g) 4 6 
That will be the 4th playlist, and the folder associated with the number 6.""")
                    continue

                local = res.get("local_dict")
                stream = res.get("stream_dict")
                folders = res.get("folder_dict")

                # This is done to preserve the original keys, which full doesnt have.
                full = local | stream | folders

                keys = folder_choice.split()

                if len(keys) != 2:
                    print("Invalid input, please enter h for the help message.")
                    continue

                # Converts baxk into ints.
                int_keys = [int(key) for key in keys]

                playlist = full.get(int_keys[0])
                folder = full.get(int_keys[1])

                err = None
                err_msg = {
                        "playlist_unfound": "No playlist found.",
                        "folder_unfound": "No folder found.",
                        "folder_is_playlist": "Selected folder was a playlist, invalid input",
                        "playlist_is_folder": "Selected playlist was a folder, invalid input",
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
                    folder.append(int_keys[0])

                    self.song_paths[int_keys[1]] = folder
                    self.saver()

                    print("\nSuccess!\n")
                else:
                    self.term_cleaner()
                    continue
                

            except (ValueError,IndexError):
                print("Invalid input.")
                continue

    #### Folder del ####

    def folder_del(self):
        while True:
            try:
                res = self.lib_print(local_only=False, folder_only=True)
                folder_dict = res.get("folder_dict")
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

                match = folder_dict.get(del_choice)
                if match is None:
                    self.term_cleaner()
                    print("Invalid input, no matches found.")
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
                        self.internal_delete(del_choice)
                        print("Successfully deleted.\n")
                        continue 
                    elif confirm == 0: 
                        print("Canceled.\n")
                        continue
                    else:
                        raise ValueError

            except ValueError:
                self.term_cleaner()
                print("Invalid input.")
                continue

    #### LIKED SONG REMOVE ####.

    def liked_remover(self, folder):
        while True:
            songs = {}
            try:

                for path in folder[2:]:
                    songs[len(songs)+1] = path
                    print(f"{len(songs)}) {os.path.basename(os.path.splitext(path)[0])}")
                if len(songs) == 0: print("No liked songs found.")
                choice = int(input("""
___________________________________________________________\\/
Select the song you want to unlike.                        |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                if choice == 0: break 
                else:
                    if choice not in range(1, len(songs)+1):
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

            except Exception:
                traceback.print_exc()

    #### PLAYLIST FROM FOLDER DEL ####

    def del_from_playlist(self):
        while True:
            try:
                res = self.lib_print(local_only=False, folder_only=True)

                folder_dict = res.get("folder_dict")
                library = res.get("full_dict")

                folder_choice = int(input("""
___________________________________________________________\\/
Please select a folder.                                    |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                if folder_choice == 0: break
                else:
                    folder = library[folder_choice]
                    if not self.folder_check(folder):
                        raise ValueError

                    del_playlist = self.folder_manager(folder)

                    if folder[0] == "liked_songs": 
                        self.liked_remover(folder)
                        continue

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
                        for key in folder[2:]:
                            (_, path, _, _,) = library[key]

                            if path == del_playlist[1]:
                                folder.remove(key)
                                self.saver()
                                print("Success!\n")
                                break

                    elif confirm == 0: break

                    else: raise ValueError

            except ValueError:
                self.term_cleaner()
                print("Invalid input")
                continue

    def edit_folder(self):
        self.term_cleaner()
        while True:
            try:
                res = self.lib_print(local_only=False, folder_only=True)
                folders = res.get("folder_dict")

                edit_choice = int(input(f"""
___________________________________________________________\\/
Please select a folder to rename.                          |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))

                selected = folders.get(edit_choice)
                if edit_choice == 0: break

                elif selected is None:
                    self.term_cleaner()
                    print("Not a valid folder.")
                    continue

                else:
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
                        self.saver()


            except ValueError:
                self.term_cleaner()
                print("Invalid input.")
                continue

    #### INTERNAL PLAYLIST EDITOR ####

    def internal_delete(self, num):
        for key, tupl in self.song_paths.items():
            # Folders are lists; therefore we can use .remove()
            if self.folder_check(tupl) and num in tupl:
                tupl.remove(num)

        del self.song_paths[num]

        # reenumerates song_paths keys
        res = {i: v for i, v in enumerate(self.song_paths.values(), start=1)}

        # empty song paths and refills with updated dict
        self.song_paths.clear()
        self.song_paths.update(res)

        self.saver()


    #### PLAYLIST SETTINGS #### 
    def playlist_settings(self):
        while True:
            try:
                choice = int(input("""
___________________________________________________________ 
▼ Folder settings ▼                                        |
                                                           |
1) Create a folder                                         |
2) Move playlist into a folder                             |
3) Delete a folder                                         |
4) Remove a playlist from a folder                         |
5) Edit a folder name                                      |
___________________________________________________________| 
▼ Playlist settings ▼                                      |
                                                           |
6) Delete a playlist from BnuuyPlayer                      |
7) Delete a playlist from disk                             |
8) Add a playlist                                          |
9) Edit a playlist name                                    |
___________________________________________________________|
▼ Other ▼                                                  |
                                                           |
10) Delete a Individual song(deletes from disk)            |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Back                                                    |
___________________________________________________________|

>>> """))

                self.term_cleaner()

                match choice:

                    #### Extra commands ####
                    case 0: 
                        """Return"""
                        break

                    #### Folder settings ####
                    case 1:
                        """Create folder"""
                        self.create_folder()

                    case 2:
                        """Move playlist to folder"""
                        self.folder_adder()
                    
                    case 3:
                        """Delete folder"""
                        self.folder_del()

                    case 4:
                        """Del plsylist fron folder"""
                        self.del_from_playlist()

                    case 5:
                        """Edit folder name"""
                        self.edit_folder()

                    #### Playlist settings ####

                    case 6:
                        self.term_cleaner()
                        """Delete a playlist"""
                        print("___________________________________________________________/\\")
                        self.lib_print(local_only=False)

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

                        if del_choice == 0: continue

                        else:
                            self.term_cleaner()

                            self.internal_delete(del_choice)

                            print("Successfully deleted!")
                            continue

                    case 7:
                        """Delete playlist from disk"""
                        confirm = int(input("""Are you sure? this is permanent.
1) Yes
0) No/Back

>>> """))

                        if confirm == 1:
                            print("___________________________________________________________/\\")
                            # Sets it to only compile and print local playlists

                            results = self.lib_print(local_only=True)
                            # assigns values
                            local_paths = results.get("local_dict")
                            countr = results.get("local_countr")
                            # lib print sets local back to False as a side effect

                            del_choice = int(input("""__________________________________________________________
Which playlist would you like to delete?                   \\/
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|

>>> """))


                            if del_choice == 0: continue

                            """Delete processer"""
                            # find the path, remember name for later
                            delname, path, _, _ = local_paths[del_choice]

                            """Recursive delete"""
                            rmtree(path)

                            """Library updater"""
                            # Reindexes and deletes selected playlist
                            self.internal_delete(del_choice)
                            print("Successfully deleted!")

                        elif confirm == 0:
                            self.term_cleaner()
                            continue

                        else:
                            print("Invalid input.")
                            continue


                    case 8: 
                        """Add a playlist"""
                        choice = self.adder_menu()

                        if choice == 0: continue # Return to last menu

                        funct = self.adders[choice]
                        funct()

                    case 9:
                        """Playlist name edit"""
                        while True:
                            try:
                                print("___________________________________________________________/\\")
                                results = self.lib_print(local_only=True)
                                countr = results.get("full_countr")
                                local_paths = results.get("full_dict")

                                rename_choice = int(input("""
___________________________________________________________\\/
Which playlist would you like to rename?                   |
___________________________________________________________|

>>> """))
                                if countr > 0 and rename_choice in range(1,countr+1):
                                    print("success")
                                    break

                            except ValueError:
                                print("Invalid input")
                                continue


                    #### OTHER ####

                    case 10:
                        """Delete song"""
                        print("unimplemented")

                    case _: raise ValueError 

            except ValueError:
                print("Invalid input!")
                traceback.print_exc()
                continue

    #### SETTINGS / NON-MUSIC ####
    def settings(self):
        while True:
            try:

                choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Toggle shuffle. (This is saved between sessions!)       |
2) Playlist sub settings                                   |
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
                        self.shuffl[1] = "activated"
                    else:
                        self.shuffl[1] = "deactivated"

                    self.term_cleaner()
                    print(f"Shuffle has been {self.shuffl[1]} \n")
                    continue

                elif choice == 2:
                    """Playlist sub settings"""
                    self.playlist_settings()


                else:
                    raise KeyError
            except (ValueError, KeyError):
                self.term_cleaner()
                traceback.print_exc()
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
        self.term_cleaner()

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
                print("\nInvalid input.")
                continue

    def start_code(self):
        while True:
            if not self.initialized:
                self.file_setup()
            else:
                self.main_menu()

bnuystart = BnuuyPlayer()
