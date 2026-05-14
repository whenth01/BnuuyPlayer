
try:
    import os, subprocess, sys, json

    import requests, yt_dlp

except ModuleNotFoundError as e:
    print(f"A dependency failed to import or is uninstalled! \n ▼ Error ▼ \n\n{e}")

def bnuy_except_hook(exctype, value, traceback):
    if exctype == KeyboardInterrupt:
        sys.exit()
    elif exctype == IsADirectoryError:
        print("""IsADirectoryError occurred!
This means you likely named a folder after one of BnuuyPlayer's jsons, please rename the folder or delete it to use BnuuyPlayer.""")
        sys.exit()
    else:
        sys.__excepthook__(exctype, value, traceback)

sys.excepthook = bnuy_except_hook


bnuy_path = os.path.dirname(__file__)


class Escape(Exception):
    pass

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



no_hint = [False]
initialized = [False]
shuffl = [False, "placeholder"]

bnuybinds = """WHEEL_UP      add volume  2
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

try:
    directory = os.path.join(bnuy_path, "bnuybinds.conf")
    if not os.path.exists(directory):
        raise FileNotFoundError

except FileNotFoundError:
    with open(directory, "w") as f:
        f.write(bnuybinds)


def initializer(initialized):
    if not initialized[0]:
        initialized[0] = True


#### TERMINAL CLEANER ####


def term_cleaner():
    os.system("cls" if os.name == "nt" else "clear")


#### KEYBINDED MENU ####


def binding_menu():

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


def adder_menu():
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
    term_cleaner()
    return choice


############# MAIN #############

#### MUSIC PLAYER ####


def audio_funct(directory):

    result = playlist_picker(song_paths, bnuy_path, shuffl, directory)
    try:
        _, _, _, _, player = result
        binding_menu()
        print("")

        try:
            subprocess.run(player, check=True)
            term_cleaner()
        except(subprocess.CalledProcessError) as e:
            print(f"Error occurred during playback! Error msg: {e}")
    except (ValueError, KeyError):
        pass


#### PLAYLIST PICKER ####
def playlist_picker(song_paths, bnuy_path, shuffl, directory):
    while True:

        try:

            countr = 0


            print("__________________________________________________________/\\")
            for num, tupl in song_paths.items():
                if len(tupl) == 3:
                    name, _, _ = tupl
                    print(f"{num}) {name}")
                    countr += 1
                else:
                    name, _, _, is_stream = tupl
                    print(f"{num}) {name} (Online stream.)")
                    countr += 1

            choice = int(input("""
__________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           |
0) back                                                    |
___________________________________________________________|

>>> """))

            countr = 0

            if choice == 0:
                term_cleaner()
                return choice, countr

            tmp_song = {}

            try:
                name, path, function = song_paths[choice]
                invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".it", ".wma"}
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
                name, path, function, is_stream = song_paths[choice]

            if is_stream:
                pass
            else:

                if len(tmp_song) < 1:
                    term_cleaner()
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
                    term_cleaner()


                elif choice == 2:
                    term_cleaner()
                    choice = int(input("""
___________________________________________________________
Enter the num of the song you'd like                       |
___________________________________________________________|

>>> """))
                    path = tmp_song[choice]


                elif choice == 0:
                    raise FileExistsError

                else:
                    raise ValueError

            if not shuffl[0]:
                player = [
                    "mpv",
                    path,
                    f"--input-conf={directory}",
                    "--profile=fast",
                    "--no-video",
                ]
            else:
                player = [
                    "mpv",
                    path,
                    f"--input-conf={directory}",
                    "--profile=fast",
                    "--no-video",
                    "--shuffle",
                ]

            term_cleaner()

            return choice, name, function, path, player

        except (KeyError, ValueError):
            term_cleaner()
            print("Invalid input.")
            continue


        except FileExistsError:
            continue


#### PLAYLISTS ####

song_paths = {}
bulk_save = {}

#### CORRUPTED HIST CREATOR ####

def corr_backup(bnuy_path):

    hist_backup1 = os.path.join(bnuy_path, "BnuyBackup1.json")
    hist_backup2 = os.path.join(bnuy_path, "BnuyBackup2.json")

    success_reads = 1

    while success_reads < 4:
        try:
            if success_reads == 1:
                with open(hist_path) as f:
                    main = f.read()
                success_reads += 1

            elif success_reads == 2:
                with open(hist_backup1) as f:
                    backup1 = f.read()
                success_reads += 1

            else:
                with open(hist_backup2) as f:
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

    input("""\nSong paths were lost! Screenshot/copy the previous or this message before continuing.


This means your entire library was likely corrupted. (the folders themselves are likely fine.)


You can rebuild your library via copy/pasting the paths and urls, then using path adder and stream/downloader if any remain.

BnuuyPlayer will backup the previous json and has just printed the json's contents to allow you to manually recover them if any remnant exists.

Enter any key to continue.""")

    num = 0

    while True:
        corr_path = os.path.join(bnuy_path, f"CorruptedBnuuyHist_{num}.json")
        corr_backup1 = os.path.join(bnuy_path, f"CorruptedBnuuyBackup_{num}.json")
        corr_backup2 = os.path.join(bnuy_path, f"CorruptedBnuuyBackup2_{num}.json")

        json_checker = os.path.isfile(corr_path)
        backup_checker = os.path.isfile(corr_backup1)
        backup_checker2 = os.path.isfile(corr_backup2)

        if json_checker or backup_checker or backup_checker2:
            num += 1
            continue

        else:
            if os.path.isfile(hist_path):
                os.rename(hist_path, corr_path)
            if os.path.isfile(hist_backup1):
                os.rename(hist_backup1, corr_backup1)
            if os.path.isfile(hist_backup2):
                os.rename(hist_backup2, corr_backup2)
            break

def processor(a):
    song_paths = a.get("0")
    initialized = a.get("1", True)
    no_hint = a.get("2")
    shuffl = a.get("3")

    while True:
        if song_paths is None:

            res = {i: v for i, v in enumerate(a.values(), start=0)}

            try:

                for key in res:
                    song_paths = res.get(key)

                    if isinstance(song_paths, dict):

                        if len(song_paths) < 1:
                            raise NewStart(bnuy_path)
                        else:
                            print("Corruption occurred, but BnuuyPlayer recovery successfully recovered your library, some entries may be missing.")

                            a[0] = song_paths
                            with open(hist_path, "w") as f:
                                json.dump(a, f, indent=2)

                                raise Escape
            except Escape:
                continue

            
            corr_backup(bnuy_path)


            raise FileNotFoundError

        if no_hint is None:
            print("No hint toggle was corrupted or deleted, defaulting to off...")
            no_hint = [False]


        if shuffl is None:
            print("Shuffle was corrupted or deleted, defaulting to off..")
            shuffl = [False, "placeholder"]

        break
    
    if len(song_paths) < 1:
        pass

    tmp_handler = {}
    err_paths = {}
    del_dict = {}

    invalid_countr = 0

    for num, tupl in song_paths.items():
        if len(tupl) == 2:
            name, combined = tupl
            tmp_handler[num] = (name, combined, audio_funct)

        elif len(tupl) == 3:
            name, combined, is_stream = tupl
            tmp_handler[num] = (name, combined, audio_funct, is_stream)

        else:
            invalid_countr += 1
            print(f"""\nFound invalid save path, was the JSON edited/corrupted?
Found {invalid_countr} invalid save paths.
Corrupted/edited path) {tupl}""")

            err_paths[len(err_paths) + 1] = tupl

        if len(tupl) == 2 and not os.path.isdir(combined):
            print(f"""\nFound a deleted or corrupted folder at {combined}
Deleting to prevent bugs..\n""")
            del_dict[num] = num, tupl

    if len(err_paths) > 0:
        print(f"Invalid saves list; {err_paths}")

    song_paths = tmp_handler

    if len(del_dict) >= 1:
        for num in del_dict:
            del song_paths[num]
        del_dict.clear()  # Delete invalid/corrupted song paths.

    res = {i: v for i, v in enumerate(song_paths.values(), start=1)}
    song_paths.clear()
    song_paths.update(res)  # Reindexes song path keys.


    return song_paths, initialized, no_hint, shuffl


#### PERSISTENT HIST CREATOR ####

try:


    hist_path = os.path.join(bnuy_path, "BnuyPlayerHist.json")
    hist_backup2 = os.path.join(bnuy_path, "BnuyBackup2.json")
    hist_backup1 = os.path.join(bnuy_path, "BnuyBackup1.json")


    if not os.path.isfile(hist_path) and not os.path.isfile(hist_backup2) and not os.path.isfile(hist_backup1):
        raise NewStart(bnuy_path)

    with open(hist_path, "r") as f:
        bulk_save = json.load(f)

    while True:

        process = processor(bulk_save)
        song_paths, initialized, no_hint, shuffl = process


        break


except(json.JSONDecodeError, AttributeError, SyntaxError, FileNotFoundError):
    print("Original JSON was corrupted, Attempting recovery..")
    
    backup_attempts = 1

    while True:

        try:

            if backup_attempts == 1:
                with open(hist_backup1, "r") as f:
                    bulk_save = json.load(f)
                break

            elif backup_attempts == 2:
                with open(hist_backup2, "r") as f:
                    bulk_save = json.load(f)
                break


            else:
                corr_backup(bnuy_path)
                initialized[0] = False
                break

        except(json.JSONDecodeError,
               SyntaxError, 
               AttributeError, 
               FileNotFoundError):
            backup_attempts += 1
            continue

    if not initialized[0]:
        pass

    else: 
        print("Recovery successful! You may keep using BnuuyPlayer as normal.\n")
        process = processor(bulk_save)
        song_paths, initialized, no_hint, shuffl = process


except (NewStart) as e:
    e.create_hist()

############# MAIN FOLDER/SETUP AREA #############


#### HISTORY ADDER ####


def saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path):
    tmp_handler = {}

    tmp_path = os.path.join(bnuy_path, "BnuyPlayerHist.json.tmp")
    hist_backup2 = os.path.join(bnuy_path, "BnuyBackup2.json")
    hist_backup1 = os.path.join(bnuy_path, "BnuyBackup1.json")

    for num, tupl in song_paths.items():
        check = len(tupl)
        if check == 3:
            name, combined, _ = tupl
            tmp_handler[num] = (name, combined)
        else:
            name, combined, _, is_stream = tupl
            tmp_handler[num] = (name, combined, is_stream)

    song_paths = tmp_handler

    bulk_save = {}

    bulk_save[0] = song_paths
    bulk_save[1] = initialized
    bulk_save[2] = no_hint
    bulk_save[3] = shuffl

    successful_saves = 0

    try:


        with open(tmp_path, "w") as f:
            json.dump(bulk_save, f, indent=2)
        os.replace(tmp_path, hist_path)
        successful_saves += 1


        with open(hist_path, "r") as mainhist, open(hist_backup1, "w") as backup1:
            backup1.write(mainhist.read())
        successful_saves += 1

        if not os.path.isfile(hist_backup1):
            pass
        else:
            with open(hist_backup1, "r") as backup1, open(hist_backup2, "w") as backup2:
                backup2.write(backup1.read())
            successful_saves += 1

    except(FileNotFoundError, OSError) as e:
        if successful_saves == 0:
            print(f"Device ERROR during save, BnuuyPlayer is unable to work properly! Error message: \n\n{e}")

        else:
            corr_backup(bnuy_path)

if initialized[0]:
    saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
else: pass

#### EXIT FUNCT ####


def exity(_):
    sys.exit()


#### PLAYLIST/PATH ADDER ####


def path_adder(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path):
    term_cleaner()
    while True:
        try:
            path_input = input("""
___________________________________________________________
▼ Valid file paths ▼                                       |
                                                           |
MacOS: /users/<your_username>/...                          |
Linux: /home/<your_username>/...                           |
Android: /storage/emulated/0/...                           |
Windows: C:\\users\\<your_username>\\...                   |
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

            is_playlist_path = os.path.isdir(path_input)

            if path_input == "0":
                break

            if not is_playlist_path:
                term_cleaner()
                print("\nDirectory dosen't exist, or you made a typo.")
                continue

            else:
                term_cleaner()
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

                    elif name_choice == "2":
                        playlist_name = os.path.basename(path_input)
                        break

                    else:
                        print("Invalid choice!")
                        continue

                song_path_len = len(song_paths) + 1
                song_paths[song_path_len] = (playlist_name, path_input, audio_funct)
                saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
                term_cleaner()
                print("Playlist successfully added!")

                initializer(initialized)

                path_input = input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Continue to BnuuyPlayer.                                |
2) Add one more path.                                      |
___________________________________________________________|

>>> """).lower()

            if path_input == "1":
                break
            elif path_input == "2":
                continue
            else:
                raise ValueError

        except ValueError:
            print("Invalid input.\n")
            continue


#### ADD/CREATE FOLDER ####


def folder_maker(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path):
    term_cleaner()
    while True:
        try:
            folder_name = input("""
___________________________________________________________
Continue to let BnuuyPlayer to make a folder.              |
                                                           |
1) Continue                                                |
2) Back                                                    |
___________________________________________________________|

>>> """)
            if folder_name == "1":
                term_cleaner()
                folder_name = input("""
___________________________________________________________
What would you like to name the playlist?                  |
___________________________________________________________|

>>> """)

                song_path = os.path.join(bnuy_path, folder_name)
                os.makedirs(song_path)

                num = len(song_paths) + 1

                song_paths[num] = (folder_name, song_path, audio_funct)
                saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
                term_cleaner()
                print(f"""\nSuccessfully created.
Path to the new playlist folder) {song_path}

You can add any song to the newly created playlist.""")

                initializer(initialized)

                break

            elif folder_name == "2":
                break

            else:
                term_cleaner()
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


def song_searcher(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path):
    term_cleaner()
    song_path_len = 0
    song_path_len += len(song_paths)
    while True:
        name = input("""
___________________________________________________________
Please enter the folder name you'd like BnuuyPlayer to find|
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) return                                                  |
___________________________________________________________|

>>> """)

        if name == "0":
            break

        results = {}
        res_len = len(results)

        try:
            for root, dirs, _ in os.walk(bnuy_path):
                if name in dirs:
                    res_len += 1

                    combined = os.path.join(root, name)
                    results[res_len] = (name, combined, audio_funct)

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

                if choice == 0:
                    for key, (name, root, _) in results.items():
                        song_path_len += 1
                        song_paths[song_path_len] = (name, root, audio_funct)
                        combined = root

                else:
                    song_path_len += 1
                    name, root, _ = results[choice]
                    song_paths[song_path_len] = (name, root, audio_funct)
                    combined = root

            elif len(results) == 1:
                song_path_len += 1
                _, combined, _ = results[1]
                song_paths[song_path_len] = results[1]

            else:
                raise UnboundLocalError

            term_cleaner()
            choice = int(input(f"""
__________________________________________________________/\\
Successfully found at {combined}!
__________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           | 
1) Return to BnuuyPlayer                                   |
2) Add another folder.                                     |
___________________________________________________________|

>>> """))
            saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
            initializer(initialized)

            if choice == 1:
                break
            elif choice == 2:
                continue
            else:
                term_cleaner()
                raise ValueError

        except UnboundLocalError:
            print("\nFolder not found.")
            continue
        except ValueError:
            print("\nInvalid input.")
            continue


#### YOUTUBE DOWNLOADER/STREAMER ####


def yt_adder(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path):
    while True:
        try:
            song_path_len = len(song_paths) + 1
            choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Download the video/playlist(may take alot of storage)   |
2) Stream the video/playlist(Online only)                  |
0) Back                                                    |
___________________________________________________________|

>>> """))

            term_cleaner()
            
            while True:

                if choice != 0:
                    try:

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
                                         "mixcloud.com",
                                         "audiomack.com"}

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

                        if url_inp == "0":
                            break

                        tmp_url = [x for x in valid_domains if x in url_inp]
                                   


                        if len(tmp_url) == 0:
                            raise requests.exceptions.InvalidURL

                        url_valid = requests.get(url_inp, timeout=10)
                        url_valid.raise_for_status()
                        
                        

                    except (requests.exceptions.ConnectionError) as e:
                        term_cleaner()
                        print(f"No internet, DNS error or refused connection, full error below. \n\n{e}")
                        continue


                    except(
                        requests.exceptions.MissingSchema,
                        requests.exceptions.InvalidSchema,
                        requests.exceptions.InvalidURL,
                        requests.exceptions.InvalidHeader,
                    ) as e:
                        term_cleaner()

                        if not str(e):
                            print("""Unsupported domain!\n 
___________________________________________________________
▼ Bnuuyplayer supports ▼                                  /\\""")

                            for domain in valid_domains:
                                print(domain)
                            print("__________________________________________________________\\/")

 
                        else:
                            print(f"Invalid URL, or an issue occurred regarding the URL occurred. Full error may be below  \n{e}")
                            continue

                    except(requests.exceptions.Timeout):
                        term_cleaner()
                        print("Timeout error, URL took too long to respond.")


                    except requests.exceptions.HTTPError as e:
                        term_cleaner()
                        print(f"An unknown error occurred, error message from the server ▼ \n\n{e}")



                    else:
                        break

                elif choice == 0:
                    break

                else:
                    print("Invalid input!")
                    continue

            if choice == 1:
                term_cleaner()
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

                        term_cleaner()
                        countr = 0
                        tmp_dict = {}

                        for num, tupl in song_paths.items():
                            if len(tupl) == 3:
                                countr += 1
                                name, _, _ = tupl
                                tmp_dict[countr] = num, tupl
                                print(f"{countr}) {name}")

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
                        if choice != 0:
                            num, (name, path, audio_funct) = tmp_dict[choice]

                        else:
                            continue

                    case 2:
                        term_cleaner()

                        while True:
                            folder_name = input("""
___________________________________________________________
What would you like to name the folder?                    |
___________________________________________________________|

>>> """)

                            try:
                                path = os.path.join(bnuy_path, folder_name)
                                os.makedirs(path)
                                break

                            except(FileExistsError):
                                term_cleaner()
                                print("Folder already exists.\n")
                                continue

                        term_cleaner()
                        disp_name = input("""
___________________________________________________________
Would you like a display name for the folder?              |
                                                           |
0) No, continue.                                           |
___________________________________________________________|

>>> """)
                        if disp_name == "0":
                            song_paths[len(song_paths) + 1] = (
                                folder_name,
                                path,
                                audio_funct,
                            )
                        else:
                            song_paths[len(song_paths) + 1] = (
                                disp_name,
                                path,
                                audio_funct,
                            )

                    case 0:
                        continue

                    case _:
                        raise ValueError

                term_cleaner()
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
___________________________________________________________|
▼ Unsupported extensions ▼                                 |
                                                           |
midi/mid                                                   |
mod, xm, s3m, it                                           |
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
                    elif ext == "0":
                        os.rmdir(path)
                        break

                    elif ext not in vid_ext:
                        yt_opts = {
                            "outtmpl": f"{path}/%(title)s.%(ext)s",
                            "format": "bestaudio/best",
                            "ignoreerrors": True,
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
                            "outtmpl": f"{path}/%(title)s.%(ext)s",
                            "format": f"bestvideo[ext={ext}]+bestaudio/best",
                        }

                    term_cleaner()
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

                    print("\nSuccessfully downloaded!\n")

                    initializer(initialized)
                    saver(
                        song_paths, initialized, shuffl, no_hint, bulk_save, hist_path
                    )
                    break

            elif choice == 2:

                if url_inp == "0":
                    break

                initializer(initialized)
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
                song_paths[song_path_len] = (
                    name_choice,
                    url_inp,
                    audio_funct,
                    is_stream,
                )
                saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
                print("Successfully added!")
                initializer(initialized)

            elif choice == 0:
                break

            else:
                raise ValueError

        except (ValueError, KeyError):
            print("\nInvalid input.")
            continue


#### ADDER DICT ####

adders = {
    0: "Skip.",
    1: path_adder,
    2: folder_maker,
    3: song_searcher,
    4: yt_adder,
}


#### SETTINGS / NON-MUSIC ####
def settings(shuffl, song_paths, adders, bulk_save, initialized, no_hint, hist_path):
    while True:
        try:

            choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Toggle shuffle. (This is saved between sessions!)       |
2) Delete a playlist.                                      |
3) Add a playlist.                                         |
0) Return.                                                 |
___________________________________________________________|

>>> """))
            term_cleaner()

            if choice == 0:
                saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
                break

            if choice == 1:
                if not shuffl[0]:
                    shuffl[0] = True
                    shuffl[1] = "activated"
                else:
                    shuffl[0] = False
                    shuffl[1] = "deactivated"

                term_cleaner()
                print(f"Shuffle has been {shuffl[1]} \n")
                continue

            elif choice == 2:
                print("___________________________________________________________/\\")
                for num, tupl in song_paths.items():
                    if len(tupl) == 3:
                        (
                            name,
                            _,
                            _,
                        ) = tupl
                        print(f"{num}) {name}")
                    else:
                        (
                            name,
                            _,
                            _,
                            _,
                        ) = tupl
                        print(f"{num}) {name} (Online streaming.)")

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

                term_cleaner()
                if del_choice == 0:
                    continue
                else:
                    del song_paths[del_choice]

                    res = {i: v for i, v in enumerate(song_paths.values(), start=1)}
                    song_paths.clear()
                    song_paths.update(res)

                    print("Successfully deleted!\n")
                    saver(
                        song_paths, initialized, shuffl, no_hint, bulk_save, hist_path
                    )

                continue

            elif choice == 3:
                choice = adder_menu()
                if choice == 0:
                    continue

                funct = adders[choice]
                funct(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path)

            else:
                raise KeyError
        except (ValueError, KeyError):
            term_cleaner()
            print("Invalid input.\n")


#### OPERATIONS ####

main_operations = {
    "1": (
        "Playlists",
        "Your library, your songs/playlists are here.         ",
        audio_funct,
    ),
    "2": (
        "Keybinds ",
        "Music player keybinds.                               ",
        binding_menu,
    ),
    "3": (
        "Settings ",
        "Your settings, this is where important functions are.",
        settings,
    ),
    "e": ("Exit     ", "Closes BnuuyPlayer.                                  ", exity),
}

#### INITIAL SETUP ####


def file_setup(initialized, song_paths, adders):

    term_cleaner()
    if not initialized[0]:
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
                choice = adder_menu()
                term_cleaner()

                if choice in range(1, 5):
                    funct = adders[choice]
                    funct(
                        song_paths,
                        initialized,
                        bnuy_path,
                        bulk_save,
                        no_hint,
                        hist_path,
                    )
                    break
                elif choice == 0:
                    initializer(initialized)
                    break

                else:
                    raise ValueError

            except ValueError:
                term_cleaner()
                print("\nInvalid Input.")
                continue


#### MAIN MENU ####


def main_menu(
    main_operations, song_paths, initialized, no_hint, hist_path, bulk_save, shuffl
):

    saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
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
        try:
            print("___________________________________________________________")
            for key, (name, _, _) in main_operations.items():
                print(f"{key}) {name}                                               |")
            print("___________________________________________________________|")
            if not no_hint[0]:
                print("""▼ Extra commands ▼                                         |
                                                           | 
h/H) Extra information, use if you're lost.                |
0) Toggle this message off/on.                             |
___________________________________________________________|""")
            choice = input(">>> ").lower()

            if choice == "h":
                term_cleaner()
                print("___________________________________________________________")
                for num, (name, hint, _) in main_operations.items():
                    print(
                        f"""{num}) {name}                                               |
Info: {hint}|
                                                           |"""
                    )
                print("___________________________________________________________|\n")
                continue

            elif choice == "0":
                term_cleaner()

                if no_hint[0]:
                    no_hint[0] = False
                else:
                    no_hint[0] = True

                saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
                print("Successfully toggled.\n")
                continue

            term_cleaner()
            name, _, function = main_operations[choice]
            if choice == "3":
                function(
                    shuffl,
                    song_paths,
                    adders,
                    bulk_save,
                    initialized,
                    no_hint,
                    hist_path,
                )
            elif choice == "2":
                function()
            else:
                function(directory)

        except KeyError:
            print("\nInvalid input.")
            continue


while True:
    if not initialized[0]:
        file_setup(initialized, song_paths, adders)
    else:
        main_menu(
            main_operations,
            song_paths,
            initialized,
            no_hint,
            hist_path,
            bulk_save,
            shuffl,
        )
