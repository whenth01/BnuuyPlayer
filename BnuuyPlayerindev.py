import os
import subprocess
import sys
import json
import threading
import time

try:
    import requests
    import yt_dlp
except ModuleNotFoundError as e:
    print(f"A dependency failed to import or is uninstalled! \n ▼ Error ▼ \n\n{e}")


#### README ####

# Inline comments like this are treated as 'How', and 'Why'
"""Docstrings like this are treated as footnotes on what something does, not why"""
#### Comments with 4 hashes are titles. ####


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
        # used when printing plsylists if it only needs local
        self.local_only = False

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

        """Method calls"""
        self.hist_creator()
        self.keybind_creator()
        counter = threading.Thread(target=self.time_counter, daemon=True)
        counter.start()
        sys.excepthook = self.bnuy_except_hook
        self.start_code()

    #### BNUUYPLAYER TIME USED COUNTER ####

    """BnuuyPlayer time used"""
    # Currently unimplemented, this will run on startup in a separate thread 
    # to show the user a stat on how long they've been using BnuuyPlayer.
    # Currently known issue) Dosent save before quit
    def time_counter(self):
        while True:
            self.time_used += 1
            time.sleep(1)
            continue


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
___________________________________________________________|

>>> """))
                if choice == 1:
                    time_elapsed = time.strftime("%H:%M:%S", time.gmtime(self.time_used))
                    self.term_cleaner()
                    print(f"You have been using BnuuyPlayer for) {time_elapsed}")

                else: break

            except ValueError: 
                self.term_cleaner()
                print("Invalid input!\n")
                continue



    ############# MAIN #############

    #### MUSIC PLAYER ####


    def audio_funct(self):
        result = self.playlist_picker()

        try:
            _, _, _, _, player = result
            print("")

            try:
                # lrc_thrd = threading.Thread(target=lrc_funct, daemon=True)
                # lrc_thrd.start()

                self.binding_menu()
                subprocess.run(player, check=True)
                self.term_cleaner()

            except(subprocess.CalledProcessError) as e:
                print(f"Error occurred during playback! Error msg: {e}")
        except (ValueError, KeyError):
            pass


    # Deprecated until further notice
    # This is being kept as it'll  be used sometime in the future, around early 2027

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


    #### LIBRARY PRINTER ####

    def lib_print(self):
        countr = 0
        local_dict = {}

        # prints every playlist/streamed playlist and song 
        # checks how long the tuple is, 3 = local, otherwise stream
        for num, tupl in self.song_paths.items():
            if len(tupl) == 3:
                name, _, _, = tupl 
                print(f"{num}) {name}")
                countr += 1
                local_dict[countr] = num, tupl

            elif len(tupl) == 4 and not self.local_only:
                name, _, _, _ = tupl 
                print(f"{num}) {name} (Online stream.)")
                countr += 1 

        self.local_only = False

        return countr, local_dict


    #### PLAYLIST PICKER ####

    def playlist_picker(self):
        while True:

            try:

                countr = 0

                self.term_cleaner()
                print("__________________________________________________________/\\")
                self.lib_print()

                choice = int(input("""
__________________________________________________________\\/
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

                # prints every local song in current song path playlist
                # splits the extension from songname, compares to invalid ext
                # if it is in invalid ext it skips, otherwise print
                try:
                    name, path, function = self.song_paths[choice]
                    invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".wma", ".lrc"}
                    for song in os.listdir(path):
                        filename, ext = os.path.splitext(song)

                        if ext not in invalid_ext:
                            filepath = os.path.join(path, song)
                            countr += 1
                            print(f"{countr}) {filename}")
                            tmp_song[countr] = filepath
                    is_stream = False

                except ValueError:
                    print(
                    "Warning: Individual song picking is unsupported for streaming due to technical limitations."
                )
                    name, path, function, is_stream = self.song_paths[choice]

                # Skips indiv song picker if its streamed
                if is_stream: pass


                # Checks if the song path dict is empty, otherwise act normal
                else:
                    if len(tmp_song) < 1:
                        self.term_cleaner()
                        print("Playlist is empty.\n")
                        continue


                    choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Play the whole playlist                                 |
2) Play one song                                           |
0) Back                                                    |
___________________________________________________________|

>>> """))

                    if choice == 1:
                        self.term_cleaner()
                        # automatically moves on, no need for extra logix


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
                            continue
                        path = tmp_song[choice]

                    # Raises escape to enter outer loop and to return.
                    elif choice == 0:
                        raise Escape

                    else:
                        raise ValueError


                player = [
                    "mpv",
                    path,
                    f"--input-conf={self.keybind_dir}",
                    "--profile=fast",
                    "--no-video"
                    ]

                # f"--input-ipc-server={self.bnuy_path}/.mpv_socket"
                # saving this here for when i have a laptop/pc.

                if self.shuffl[0]:
                    player.append("--shuffle")

                self.term_cleaner()

                return choice, name, function, path, player

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

    #### LOADSAVE FILE LOADER ####

    def processor(self):
        self.song_paths = self.bulk_save.get("0")
        self.initialized = self.bulk_save.get("1", True)
        self.no_hint = self.bulk_save.get("2")
        self.shuffl = self.bulk_save.get("3")
        self.time_used = self.bulk_save.get("4")

        while True:
            """Song paths recoverer"""
            if self.song_paths is None:

                # Reenumerates and creates a temp dict for recovery
                res = {i: v for i, v in enumerate(self.bulk_save.values(), start=0)}

                try:

                    for key in res:
                        # searches for a dict(the song paths is the only dict)
                        self.song_paths = res.get(key)

                        if isinstance(self.song_paths, dict):

                            # If theres nothing in their library, assume newstart
                            if len(self.song_paths) < 1:
                                raise NewStart(self.bnuy_path)

                            else:
                                print("Corruption occurred, but BnuuyPlayer recovery successfully recovered your library, some entries may be missing.")

                                """Writes recovered song paths to disk and esc"""
                                self.bulk_save[0] = self.song_paths
                                with open(self.hist_path, "w") as f:
                                    json.dump(self.bulk_save, f, indent=2)

                                    # File closes as escape is raised
                                    # Escapes and reattempts load
                                    raise Escape
                # Attempts to recheck the history to ensure integrity
                except Escape:
                    continue


                self.corr_backup()

                # Only reachable song_paths is None and theres no dict in bulk_save
                raise RareError

            # defaults to False if no_hint is missing
            if self.no_hint is None:
                print("No hint toggle was corrupted or deleted, defaulting to off...")
                self.no_hint = False


            # same as above for shuffle
            if self.shuffl is None:
                print("Shuffle was corrupted or deleted, attemping recovery.")
                self.shuffl = [False, "placeholder"]

            if self.time_used is None:
                print("debug, replace with recovery")
                self.time_used = 0

            break

        """Gives up if no playlists"""
        # If the song paths are empty, give up, otherwise keep recovering
        if len(self.song_paths) < 1:
            pass


        tmp_handler = {}
        err_paths = {}
        del_dict = {}

        invalid_countr = 0
        
        """Playlist corr/valid sorter"""
        # Attempts to recover playlists, if it fails or the values are too high
        # it adds 1 to invalid countr, then adds it to err paths
        # if the playlist is recovered successfully, its put into tmp handler
        for num, tupl in self.song_paths.items():
            if len(tupl) == 2:
                name, combined = tupl
                tmp_handler[num] = (name, combined, self.audio_funct)

            elif len(tupl) == 3:
                name, combined, is_stream = tupl
                tmp_handler[num] = (name, combined, self.audio_funct, is_stream)

            else:
                invalid_countr += 1
                print(f"""\nFound invalid save path, was the JSON edited/corrupted?
Found {invalid_countr} invalid save paths.
Corrupted/edited path) {tupl}""")

                err_paths[len(err_paths) + 1] = tupl

            """Deleted folders compiler"""
            # compiles any deleted folders outside of BnuuyPlayer
            # only does this for locals playlists
            if len(tupl) == 2 and not os.path.isdir(combined):
                print(f"""\nFound a deleted or corrupted folder at {combined}
Deleting to prevent bugs..\n""")
                del_dict[num] = num, tupl 

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
        try:
            """Hist creator/checker/loader"""
            # Pulled from self, checks if the jsons actually exists.
            # If it doesnt exist, raise NewStart
        
            if not os.path.isfile(self.hist_path) and not os.path.isfile(self.hist_backup2) and not os.path.isfile(self.hist_backup1): 
                raise NewStart(self.bnuy_path)

            with open(self.hist_path, "r") as f:
                self.bulk_save = json.load(f)

            try: self.processor()
            # No song paths found in manual recov path attempts corr backup
            except RareError: self.corr_backup()



        except(json.JSONDecodeError, AttributeError, SyntaxError, FileNotFoundError):
            print("Original JSON was corrupted, Attempting recovery..")

            backup_attempts = 1

            while True:


                """JSON backup loader/corrupted backuper"""
                # Attempts to load backups, if all fail it'll initiate unrecoverable
                # backups and allow the user to manually recover,
                # Loops until it hits above 2(for both backups) or a successful load
                # break Only runs if no exception is raised by JSON 
                # If break runs, it likely means the load was successful
                try:

                    # Attempts to load 1st backup
                    if backup_attempts == 1:
                        with open(self.hist_backup1, "r") as f:
                            self.bulk_save = json.load(f)
                        break

                    # Attempts to load 2nd backup
                    elif backup_attempts == 2:
                        with open(self.hist_backup2, "r") as f:
                            self.bulk_save = json.load(f)
                        break

                    # No working backup found, giveup and init corr_backup
                    else:
                        self.corr_backup()
                        self.initialized = False
                        break

                except(json.JSONDecodeError,
                       SyntaxError, 
                       AttributeError, 
                       FileNotFoundError):
                    backup_attempts += 1
                    continue

        except NewStart as e:
            e.create_hist()

            # This works just by stopping the funct and allowing the if/else at the bottom pick.
            if not self.initialized:
                pass

            else: 
                print("Recovery successful! You may keep using BnuuyPlayer as normal.\n")
                try: self.processor()

                # corr_backup already handles user messaging and files 
                # therefore pass is used
                except RareError: pass



    ############# MAIN FOLDER/SETUP AREA #############


    #### HISTORY ADDER ####


    def saver(self):
        tmp_handler = {}
        self.bulk_save = {}
        tmp_path = os.path.join(self.bnuy_path, "BnuyPlayerHist.json.tmp")

        """Save compiler"""
        # Compiles every playlist into a temp dict to be saved.
        for num, tupl in self.song_paths.items():
            check = len(tupl)
            if check == 3:
                name, combined, _ = tupl
                tmp_handler[num] = (name, combined)
            else:
                name, combined, _, is_stream = tupl
                tmp_handler[num] = (name, combined, is_stream)

        # Assigns a local version of self.song_paths with audio_funct stripped
        local_song_paths = tmp_handler

        """Bulk save build"""
        # Compiles bulk save.
        self.bulk_save[0] = local_song_paths
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

            if not os.path.isfile(self.hist_backup1):
                pass

            # If it was successful, read backup1, write it to backup2
            else:
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
                    self.song_paths[len(self.song_paths)+1] = (playlist_name, path_input, self.audio_funct)

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

                    self.song_paths[len(self.song_paths) + 1] = (folder_name, song_path, self.audio_funct)
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
            song_path_len = 0 
            countr = 0
            song_path_len += len(self.song_paths)

            
            """Folder printer"""
            # For every file in bnuuyplayer's folder, if dir print it
            # if theres no folders, break out
            print("""
___________________________________________________________
▼ Folders found in current dir ▼                           |
___________________________________________________________|
                                                           \\/""")
            
            for file in os.listdir(self.bnuy_path):

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
                        results[res_len] = (name, combined, self.audio_funct)


                # If multiple folders are found, print every root and key 
                # and ask the user for one of them, or all
                if len(results) > 1:
                    print("\nMultiple folders found!")

                    while True:
                        for key, (name, root, _) in results.items():
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
                        for key, (name, root, _) in results.items():
                            song_path_len += 1
                            self.song_paths[song_path_len] = (name, root, self.audio_funct)
                            combined = root

                    # write chosen one into playlists
                    else:
                        song_path_len += 1
                        name, root, _ = results[choice]
                        self.song_paths[song_path_len] = (name, root, self.audio_funct)
                        combined = root

                # if only 1 is found, write immediately
                elif len(results) == 1:
                    song_path_len += 1
                    _, combined, _ = results[1]
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

    # d contains information from yt-dlp, which my code then gets the informatuin
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

                print(f"\n\nAttempting to download lyrics..")


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


                if lyric is not None:
                    with open(lrc_path, "w") as f:
                        f.write(lyric)
                # 404 means no lyrics found as per lrclib responses

            elif lrc_get.status_code == 404:
                print("\n No lyrics found!")

            else:
                print(f"\nUnknown error) {lrc_get.status_code}")

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
                    choice = int(input("""
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
                    match choice:
                        case 1:

                            self.term_cleaner()

                            # prints every playlist and writes to tmp_dict
                            self.local_only = True

                            modular_print = self.lib_print()

                            countr, tmp_dict = modular_print

                            # if no playlists this runs
                            if len(tmp_dict) < 1:
                                print("\nNo playlists currently available.")

                            choice = int(input("""
___________________________________________________________
Pick a playlist.                                           |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return.                                                 |
___________________________________________________________|

>>> """))
                            # selects the playlist from tmp via dict unpacking
                            if choice != 0:
                                num, (name, path, _) = tmp_dict[choice]

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
                            if disp_name == "0":
                                self.song_paths[len(self.song_paths) + 1] = (
                                    folder_name,
                                    path,
                                    self.audio_funct,
                                )
                            # else use disp name
                            else:
                                self.song_paths[len(self.song_paths) + 1] = (
                                    disp_name,
                                    path,
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

                        vid_ext = {
                        "mp4",
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

                        if "." in ext:
                            print("Invalid ext, do not include a dot!")
                            continue

                        # deletes folder to prevent orphaned folders
                        elif ext == "0":
                            if choice == 2:
                                os.rmdir(path)
                            break

                        # if its a audio format; use postprocessors, else dont
                        elif ext not in vid_ext:
                            yt_opts = {
                                "outtmpl": f"{path}/%(title)s.%(ext)s",
                                "format": "bestaudio/best",
                                "progress_hooks": [self.yt_hook],
                                "ignoreerrors": True,
                                "no_warnings": True,
                                "postprocessors": [
                                    {
                                        "key": "FFmpegExtractAudio",
                                        "preferredcodec": ext,
                                    }
                                ],
                            }

                        else:
                            yt_opts = {
                                "ignoreerrors": True,
                                "no_warnings": True,
                                "outtmpl": f"{path}/%(title)s.%(ext)s",
                                "progress_hooks": [self.yt_hook],
                                "format": f"best[ext={ext}]",
                            }

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
                        self.audio_funct,
                        is_stream,
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


    #### SETTINGS / NON-MUSIC ####
    def settings(self):
        while True:
            try:

                # TODO: 
                # 1) Move playlist settings into subsection
                choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Toggle shuffle. (This is saved between sessions!)       |
2) Delete a playlist from BnuuyPlayer.                     |
3) Delete a playlist from disk.                            |
4) Delete a song from disk                                 |
5) Add a playlist.                                         |
6) Add a song to a playlist individually                   |
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
                    """Delete playlist from BnuuyPlayer"""
                    print("___________________________________________________________/\\")
                    self.lib_print()

                    del_choice = int(input("""
___________________________________________________________
                                                           \\/
Which would you like to delete?                            |
(This only deletes the playlist from BnuuyPlayer!)         |
___________________________________________________________|
▼ Extra commands ▼                                         |
0) return                                                  |
___________________________________________________________|

>>> """))

                    self.term_cleaner()
                    if del_choice == 0:
                        continue
                    else:
                        del self.song_paths[del_choice]

                        # reenumerates song_paths keys
                        res = {i: v for i, v in enumerate(self.song_paths.values(), start=1)}
                        self.song_paths.clear()
                        self.song_paths.update(res)

                        print("Successfully deleted!\n")
                        self.saver()

                        continue

                elif choice == 3:
                    """Delete playlist from disk"""
                    print("Delete playlist from disk unimplemented")
                    continue

                elif choice == 4:
                    """Delete individual song"""
                    print("Del song from disk unimplemented")
                    continue

                elif choice == 5:
                    """Add a playlist"""
                    choice = self.adder_menu()
                    if choice == 0:
                        continue

                    funct = self.adders[choice]
                    funct()

                elif choice == 6:
                    """Add indiv song to playlist"""
                    print("unimplemented")

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
0) Toggle this message off/on.                             |
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

                elif choice == "0":
                    self.term_cleaner()

                    # Toggles no hint off/on
                    self.no_hint = not self.no_hint

                    # writes to disk
                    self.saver()
                    print("Successfully toggled.\n")
                    continue

                self.term_cleaner()
                name, _, function = self.main_operations[choice]

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
