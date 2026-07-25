import os
from datetime import timedelta

####### GENERAL PURPOSE MENUS #######

#### TERMINAL CLEARER ####

def term_cleaner():
    os.system("cls" if os.name == "nt" else "clear")

#### GENERAL INVALID INPUT PRINTS ####

def general_exception(extra_text=""):
    term_cleaner()
    print(f"Invalid input! :(")
    if extra_text != "":
        print(extra_text)
    return

def special_exception(err_text):
    term_cleaner()
    print(err_text)
    return

def bad_folder_names():
    term_cleaner()
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
DO_NOT_DELETE.json                                         |
bnuybinds.conf                                             |
                                                           |
___________________________________________________________|""")
    return

#### GENERAL INPUTS ####
def intput():
    select = int(input("\n>>> "))
    return select

def strput():
    select = input("\n>>> ")
    return select

#### KEYBINDING MENU ####

def binding_menu():
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


#### ADD STUFF METHODS MENU ####

def adder_menu():
    # Asks the user for playlist method, returns to caller
    """Playlist method menu and choice returner"""
    print("""
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
___________________________________________________________|""")

    choice = intput()

    term_cleaner()
    return choice
    
#### TIMER PRINTER ####

def time_print(mode, time):
    time_elapsed = str(timedelta(seconds=time))
    term_cleaner()

    print(f"You have been {mode} BnuuyPlayer for) {time_elapsed}")
    return

####### MAIN MENU #######

def easter_egg_menu(easter_eggs):
    print("""
___________________________________________________________
▼ EasterEggs ▼                                            /\\""")

    for key, (name, hint, info, found) in easter_eggs.items():
        if found: found = "You found this Easter Egg!:3"
        else: 
            found = "Not found yet"
            info = "Find this Easter Egg to view it's info"

        print(f"""
{key}) {name} ({found})
Hint) {hint}
Info) {info}""")

    print("""
___________________________________________________________\\/ 
▼ Statistics ▼                                             |
                                                           |
1) Amount of time you have been using Bnuuyplayer for      |
2) Amount of time you have been playing music for.         |
0) Return                                                  |
___________________________________________________________|""")
    choice = strput()
    term_cleaner()
    return choice

def kitty():
    print("""
 ⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⡴⣆⠀⠀⠀⠀⠀⣠⡀⠀⠀⠀⠀⠀⠀⣼⣿⡗⠀⠀⠀⠀
⠀⠀⠀⣠⠟⠀⠘⠷⠶⠶⠶⠾⠉⢳⡄⠀⠀⠀⠀⠀⣧⣿⠀⠀⠀⠀⠀
⠀⠀⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣤⣤⣤⣤⣤⣿⢿⣄⠀⠀⠀⠀
⠀⠀⡇⠀⢀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣧⠀⠀⠀⠀⠀⠀⠙⣷⡴⠶⣦
⠀⠀⢱⡀⠀⠉⠉⠀⠀⠀⠀⠛⠃⠀⢠⡟⠂⠀⠀⢀⣀⣠⣤⠿⠞⠛⠋
⣠⠾⠋⠙⣶⣤⣤⣤⣤⣤⣀⣠⣤⣾⣿⠴⠶⠚⠋⠉⠁⠀⠀⠀⠀⠀⠀
⠛⠒⠛⠉⠉⠀⠀⠀⣴⠟⣣⡴⠛⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠛⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀""")

def proto():
    print(":3 beepboppbeep")


def open_top_bottom_menu():
    print("""
___________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           |
a) Even more commands                                      |
0) Return                                                  |
___________________________________________________________|""")
    choice = strput()
    term_cleaner()
    return choice.lower()

####### MOVE FILE METHOD MENUS #######

def move_file_menu():
    print("""
___________________________________________________________\\/
Please select the location you'd like to move the song to. |
                                                           |
0) Return.                                                 |
___________________________________________________________|""")

    select = intput()
    term_cleaner()
    return select
    
def confirm(path, dest_path):
    print(f"""
___________________________________________________________ 
Are you sure?                                              /\\
Source) {path}
Destination) {dest_path}
___________________________________________________________\\/
▼ Commands ▼                                               |
                                                           |
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|""")
    confirm = intput()
    term_cleaner()

    return confirm


####### CMD HANDLER METHOD MENUS #######

def cmd_handler_del_confirm(path):
    print(f"""
__________________________________________________________/\\
Are you sure? you are deleting) {os.path.basename(os.path.splitext(path)[0])}
                                                          \\/
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|""")
    confirm = strput()
    term_cleaner()
    return confirm
    
def cmd_handler_copy_confirm(path):
    print(f"""
___________________________________________________________\\/
Select the playlist you'd like to copy the song to.        /\\
Selected file) {os.path.basename(os.path.splitext(path)[0])}
                                                           \\/
0) Return                                                  |
___________________________________________________________|""")

    select = intput()
    term_cleaner()
    return select

   
####### BULK MOVER MENUS #######

def bulk_move_select():
    print("""
___________________________________________________________\\/
Please select a playlist to move the song(s) into.         |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    playlist_select = intput()
    term_cleaner()
    return playlist_select

def bulk_move_confirm(params, playlist):
    print(f"""
___________________________________________________________
Are you sure?                                             /\\
You are moving {len(params)} file(s) (not including lyric files)
into {playlist}
                                                          \\/
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|""")

    confirm = strput()
    term_cleaner()
    return confirm


####### BULK COPY MENUS #######

def bulk_copy_dest_menu():
    print("""
___________________________________________________________\\/
Select a playlist to copy the files into.                  |
(note: This may take up alot of storage!)                  |
                                                           |
0) Return                                                  |
___________________________________________________________|""")
    dest_path = intput()

    term_cleaner()
    return dest_path

def bulk_copy_confirm(info):
    mb = info.get("mb")
    gb = info.get("gb")

    if int(gb) == 0: gb = "Less than 1 GB"
    else: gb = int(gb)

    playlist = info.get("playlist")
    params = info.get("params")
   
    print(f"""
__________________________________________________________/\\
Are you sure? you are copying {len(params)} files (excluding lyric files)
Copy size in megabytes) {int(mb)}
Copy size in gigabytes) {gb}
into the playlist) {playlist}

1) Continue                                               \\/
0) Return                                                  |
___________________________________________________________|""")
    confirm = strput()

    term_cleaner()
    return confirm

####### METADATA BULK DELETE MENUS #######

def bulk_del_confirm(params):
    print(f"""
___________________________________________________________
Are you sure? This is permanent.                          /\\
You are deleting {len(params)} files(excluding lyric files).
                                                          \\/
1) Continue                                                |
0) Return                                                  |
___________________________________________________________|""")
    confirm = intput()

    term_cleaner()
    return confirm

####### BASIC INVESTIBUN #######

def investibun_main():
    print("""___________________________________________________________
Search bnuuyplayer for a song/playlist.                    |
                                                           |
1) Search for songs                                        |
2) Search for Playlists (note: streamed songs are here)    |
0) Return                                                  |
___________________________________________________________|""")
    search_select = strput()

    term_cleaner()
    return search_select

def investibun_query():
    print("""
___________________________________________________________ 
Enter the name of what you'd like to find.                 |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    query = strput()
    term_cleaner()
    return query

def basic_result_print(info):
    playlist_handler = info.get("playlist_handler")
    entries = info.get("entries")
    keys = info.get("disp_keys")
    search = info.get("search")
    db = info.get("playlists")

    if playlist_handler:
        """Playlist printer"""
        print("""
___________________________________________________________
▼ Closest playlist matches ▼                              /\\\n""")
        if len(search) == 0:
            print("No matches found! :(")
        for num, (path, is_stream, name, og_key, disp_name) in entries.items():
            found_disp_key = False

            for disp_key, (og_saved_key, is_folder) in keys.items():
                # this resolves the display key for the user's convenience
                if is_folder: continue

                if og_key == og_saved_key: 
                  key = disp_key
                  found_disp_key = True
                  break

            if not found_disp_key:
                  key = "No match found :("

            if is_stream and name in search: 
                print(f"""{num}) {disp_name} (Online stream.)
(located at {key})\n""")

            elif name in search: 
                print(f"""{num}) {disp_name}
(located at {key})\n""")

    else:
        """Song paths printer"""

        print("""
___________________________________________________________ 
▼ Closest song matches ▼                                  /\\\n""")
        for key, names in entries.items():
            playlist_name, _, _, _, = db[key]

            found_disp_key = False
            for disp_key, (og_key, is_folder) in keys.items():
                # same basic function as above :3
                if is_folder: continue

                if key == og_key:
                    key = disp_key
                    found_disp_key = True
                    break
            if not found_disp_key:
                key = "No match found :("

            for song_name in names:
                if song_name in search:
                    print(f"""{song_name}
Located at
Playlist name) {playlist_name}
Playlist key) {key}\n""")

    print("__________________________________________________________\\/")

####### ADVANCED INVESTIBUNNY MENUS #######
def advanced_select_query():
    print("""
___________________________________________________________ 
▼ Advanced search doesnt support ▼                         |
                                                           |
.webm .mkv .mod .xm .s3m .it .mid .midi                    |
.avi .mov .mpg .mpeg .ts .flv .3gp                         |
And advanced search doesnt look through streamed entries.  |
___________________________________________________________|
___________________________________________________________
Enter a tag and what you'd like to search.                 |
E.g) artist [your query]                                   |
___________________________________________________________|
▼ Tags ▼                                                   |
                                                           |
artist                                                     |
album                                                      |
title                                                      |
genre                                                      |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    selection = strput()
    term_cleaner()
    return selection

def advanced_result_print(results, playlists, keys):
    print("""
___________________________________________________________
▼ Closest results ▼                                       /\\""")
    for num, res in results.items():
        """tuple collection"""
        data_dict = res[0]
        song_path = res[1]
        location = res[2]

        # thats the default value if nothing is found
        disp_location = "None found :("
        for disp_key, (og_key, is_folder) in keys.items():
            if is_folder: continue

            if location == og_key:
                disp_location = disp_key
                break

        """metadata collection"""
        artist = data_dict.get("artist")
        title = data_dict.get("title")
        album = data_dict.get("album")

        print(f"""
Artist(s): {artist}
Title: {title}
Album: {album}
Playlist name: {playlists[location][0]} 
Playlist key: {disp_location}""")
    return

def advanced_result_selection():
    print("""
__________________________________________________________\\/
1) Move every result into a playlist (may take some time.)|
2) Copy every result into a playlist (will take storage)  |
3) Delete every result. (may take some time)              |
4) Play every result                                      |
0) Return                                                 |
__________________________________________________________|""")
    select = strput()
    term_cleaner()
    return select


####### LOCAL LYRIC DOWNLOADER MENUS #######

def lrc_dl_confirm():
    print("""
___________________________________________________________
Are you sure? this may take a while.                       |
                                                           |
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|""")

    confirm = strput()
    term_cleaner()
    return confirm

####### PLAYLIST PICKER #######

def playlist_main_menu():
    print("""__________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           |
s) Search                                                  |
as) Advanced Search (may be slow)                           \\
dl) Download lyrics for existing songs(note: this relies on metadata)
0) back                                                     /
___________________________________________________________|""")

    select = strput()
    term_cleaner()
    return select

def song_picker_menu():
    print("""
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
___________________________________________________________|""")

    select = strput()
    term_cleaner()
    return select


####### CORR BACKUP #######

def corr_last_stand(main, backup1, backup2):
    print(f"""MAIN HIST: {str(main)}

BACKUP1: {str(backup1)}

BACKUP2: {str(backup2)}""")

    input("""\nYour lib was corrupted! Screenshot/copy the previous or this message before continuing.


This means your entire library was likely corrupted. (the folders themselves are likely fine.)


You can rebuild your library via copy/pasting the paths and urls, then using path adder and stream/downloader if any remain.

BnuuyPlayer will backup the previous json and has just printed the json's contents to allow you to manually recover them if any remnant exists.

Enter any key to continue.""")


####### ADDERS #######

## PATH ADDER
def path_input():
    print("""
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

Please input a path to a folder.""")

    path = strput()
    term_cleaner()
    return path

def path_playlist_name():
    print("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Create a display name.                                  |
2) Use the folder name.                                    |
___________________________________________________________|""")

    name = strput()
    term_cleaner()
    return name

def path_final_menu():
    print("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Add one more path.                                      |
0) Return to BnuuyPlayer main menu                         |
___________________________________________________________|""")
    next_thing = strput().lower()
    term_cleaner()
    return next_thing

## FOLDER MAKER

def allow_folder_creation():
    print("""
___________________________________________________________
Continue to let BnuuyPlayer to make a folder.              |
                                                           |
1) Continue                                                |
0) Back                                                    |
___________________________________________________________|""")

    confirm = strput()
    term_cleaner()
    return confirm

def new_folder_name():
    print("""
___________________________________________________________
What would you like to name the playlist?                  |
___________________________________________________________|""")

    name = strput()
    term_cleaner()
    return name

def success_print(path):
    print(f"""\nSuccessfully created.
Path to the new playlist folder) {path}

You can add any song to the newly created playlist.""")

## FOLDER SEARCHER

def main_folder_search(bnuy_dir):
    """Folder printer"""
    # For every file in bnuuyplayer's folder, if dir print it
    countr = 0
    print("""
___________________________________________________________
▼ Folders found in current dir ▼                           |
___________________________________________________________|
                                                           \\/""")
            
    for file in os.listdir(bnuy_dir):

        file = os.path.join(bnuy_dir, file)
        if os.path.isdir(file):
            print(f"{os.path.basename(os.path.splitext(file)[0])}")
            countr += 1

    if countr == 0:
        print("No folders found! please use one of the other methods.")


    print("""___________________________________________________________\\/
Please enter the folder you'd like to select               |
 __________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) return                                                  |
___________________________________________________________|""")

    name = strput()
    term_cleaner()
    return name

def multi_folder_found():
    print("""
___________________________________________________________
Which one is correct? If all are, enter "a"                |
                                                           |
0) Return                                                  |
___________________________________________________________|""")
    select = strput()
    term_cleaner()
    return select.lower()

def folder_success(path):
    print(f"""
__________________________________________________________/\\
Successfully found at {path}! :3
__________________________________________________________\\/
▼ Extra commands ▼                                         |
                                                           | 
1) Add another folder                                      |
0) Return to BnuuyPlayer.                                  |
___________________________________________________________|""")

    next_thingy = intput()
    term_cleaner()
    return next_thingy

## YT-DLP ADDER 

def stream_or_dl():
    print("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Download the video/playlist(may take alot of storage)   |
2) Stream the video/playlist(Online only)                  |
0) Back                                                    |
___________________________________________________________|""")

    choice = intput()
    term_cleaner()
    return choice

def url_input():
    print("""
___________________________________________________________
Enter a url                                                |
                                                           |
___________________________________________________________|         
▼ Extra commands ▼                                         |
                                                           |
0) Back/cancel                                             |
___________________________________________________________|""")

    url = strput()
    term_cleaner()
    return url

def print_site_whitelist(valid_domains):
    term_cleaner()
    print("""Unsupported domain!\n 
___________________________________________________________ 
▼ Bnuuyplayer supports ▼                                  /\\""")
    for domain in valid_domains:
        print(domain)

    print("__________________________________________________________\\/")

# Download route
def download_selection():
    print("""
___________________________________________________________
Where would you like to download the file(s)?              |
___________________________________________________________|
▼ Commands ▼                                               |
                                                           |
1) Put the song(s) in a existing local playlist.           |
2) Allow BnuuyPlayer to make a folder.                     |
0) Return.                                                 |
___________________________________________________________|""")

    selection = intput()
    term_cleaner()
    return selection

def pick_playlist_dl():
    print("""
___________________________________________________________
Pick a playlist.                                           |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return. (Note: this return's behavior will be redone)   |
___________________________________________________________|""")

    playlist = intput()
    term_cleaner()
    return playlist

def pick_new_folder_name():
    print("""
___________________________________________________________
What would you like to name the folder?                    |
___________________________________________________________|""")

    name = strput()
    term_cleaner()
    return name

def disp_name_select():
    print("""
___________________________________________________________
Would you like a display name for the folder?              |
                                                           |
1) No, continue.                                           |
0) Return                                                  |
___________________________________________________________|""")

    disp_name = strput()
    term_cleaner()
    return disp_name

def file_extension_select():
    print("""
___________________________________________________________
Enter the file extension you'd like.                       |
___________________________________________________________|
▼ Recommended extensions ▼                                 |
                                                           |
mp3     (Audio)                                            |
m4a     (Audio)                                            |
mp4     (Video)                                            |
___________________________________________________________|
▼ Unsupported extensions ▼                                 |
                                                           |
midi/mid                                                   |
mod, xm, s3m                                               |
wma                                                        |
___________________________________________________________|
▼ Extra commands ▼                                         |
0) Return                                                  |
___________________________________________________________|

Warning: Do not include a dot when entering the file extension.""")

    ext = strput()
    term_cleaner()
    return ext

# Stream route

def streamed_playlist_name():
    print("""
___________________________________________________________
Enter a name.                                              |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    name = strput()
    term_cleaner()
    return name

####### BNUUYFOLDERS #######

### CREATE BNUUYFOLDER
## Make BnuuyFolder
def new_bnuuyfolder_name():
    print("""
___________________________________________________________ 
Enter a name for the BnuuyFolder                           |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    name = strput()
    term_cleaner()
    return name

def new_bnuuyfolder_made():
    print("""Successfully created BnuuyFolder!\n 
___________________________________________________________ 
▼ Commands ▼                                               |
                                                           |
1) Create another folder                                   |
0) Return                                                  |
___________________________________________________________|""")

    next_thingy = strput()
    term_cleaner()
    return next_thingy

### Add to BnuuyFolder

def select_playlist_folder():
    print("""
___________________________________________________________\\/
Enter a playlist num then a BnuuyFolder num (e.g, 4 6)     |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
h) Help                                                    |
___________________________________________________________|""")

    selection = strput()
    term_cleaner()
    return selection

def bnuuyfolder_add_help_text():
    term_cleaner()
    print("""
▼ The valid structure is ▼
(playlist number) (folder number) 
separated by a space.

e.g) 4 6 
That will be the 4th playlist, and the folder associated with the number 6.""")

def bnuuyfolder_confirm_add(playlist_name, folder_name):
    print(f"""
___________________________________________________________/\\
You will be adding {playlist_name} (playlist/song)
into {folder_name} (folder)
                                                           \\/
Is this correct?                                           |
___________________________________________________________|
1) Continue.                                               |
0) Return.                                                 |
___________________________________________________________|""")

    select = strput()
    term_cleaner()
    return select

### BnuuyFolder delete 

def delete_bnuuyfolder_selection():
    print("""
___________________________________________________________\\/
Which folder would you like to delete?                     |
___________________________________________________________|
0) Return                                                  |
___________________________________________________________|""")

    selected = intput()
    term_cleaner()
    return selected

def delete_bnuuyfolder_confirm(name):
    print(f"""
__________________________________________________________/\\
You are deleting) {name}                                

Are you sure? this is permanent.                          \\/
___________________________________________________________|
1) Delete                                                  |
0) Return                                                  |
___________________________________________________________|""")

    confirm = intput()
    term_cleaner()
    return confirm

## Delete a playlist 
def del_select_bnuuyfolder():
    print("""
___________________________________________________________\\/
Please select a folder.                                    |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    select = intput()
    term_cleaner()
    return select

def del_confirm(playlist, folder):
    print(f"""
__________________________________________________________/\\
You will be deleting {playlist} inside {folder}
                                                          \\/   
Are you sure? this will move the playlist out.             |
___________________________________________________________|
1) Confirm                                                 |
0) Return                                                  |
___________________________________________________________|""")

    confirm = intput()
    term_cleaner()
    return confirm

## Rename bnuuyfolder
def bnuuyfolder_rename_select():
    print("""
___________________________________________________________\\/
Please select a folder to rename.                          |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    select = intput()
    term_cleaner()
    return select

def bnuuyfolder_rename(old_name):
    print(f"""
_________________________________________________________/\\
Current name) {old_name}
Enter a new name below                                   \\/
                                                          |
0) Return                                                 |
__________________________________________________________|""")

    name = strput()
    term_cleaner()
    return name

####### SITE HANDLING #######

def site_printer(valid_domains):
        site_amount = 0
        domains = {}
        print("""
___________________________________________________________
▼ Current sites ▼                                          /\\""")

        for site in valid_domains:
            site_amount += 1
            print(f"{site_amount}) {site}")
            domains[site_amount] = site

        if len(valid_domains) < 1:
            print("No sites whitelisted!:(")

        return site_amount, domains

## WHITELIST MENUS
def whitelist_site_main():
    print("""
___________________________________________________________\\/
▼ Select what to do. ▼                                     \\
NOTE: Adding a site requires the site's name, like shown above.
                                                           /
1) Add a new site to the whitelist                         |
2) Delete a site from the whitelist                        |
0) Return                                                  |
___________________________________________________________|""")

    select = intput()
    term_cleaner()
    return select

# ADD ROUTE
def enter_new_site():
    print("""
___________________________________________________________
Enter the new site name.                                   |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    site = strput()
    term_cleaner()
    return site

# DEL ROUTE

def del_site_select():
    print("""
___________________________________________________________
Please select the site you'd like to remove.               |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    site = strput()
    term_cleaner()
    return site

def del_site_confirm(domains, del_site):
    print(f"""
Are you sure? you are removing {domains[del_site]}

1) Continue
0) Return""")

    select = strput()
    term_cleaner()
    return select


####### LIKED SONGS HANDLING#######

## Liked songs remover
def liked_songs_remover_print(folder):
    songs = {}
    no_songs = False
    print("___________________________________________________________/\\")

    for path in folder[2:]:
        songs[len(songs)+1] = path
        print(f"{len(songs)}) {os.path.basename(os.path.splitext(path)[0])}")

    if len(songs) == 0:
        print("No liked songs found.")
        no_songs = True

    print("""
___________________________________________________________\\/
Select the song you want to unlike.                        |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    choice = intput()
    term_cleaner()
    return songs, no_songs, choice

####### REMOVE PLAYLIST #######

def remove_playlist():
    print("""
___________________________________________________________ 
                                                           \\/
Which would you like to delete?                            |
(This only deletes the playlist from BnuuyPlayer!)         |
___________________________________________________________|
▼ Extra commands ▼                                         |
0) return                                                  |
___________________________________________________________|""")

    selection = intput()
    term_cleaner()
    return selection

def confirm_remove(playlist_name):
    print(f"""Are you sure?
You are removing {playlist_name}

1) Confirm
0) Return""")
    confirm = intput()
    term_cleaner()
    return confirm

def delete_playlist_selection():
    print("""___________________________________________________________\\/
Which playlist would you like to delete?                   |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    selection = intput()
    term_cleaner()
    return selection

def delete_confirm(delname):
    print(f"""
___________________________________________________________/\\
Are you sure? you are deleting) {delname}
This is permanent.                                         \\/
                                                           | 
1) Delete                                                  |
0) Return                                                  |
___________________________________________________________| """)

    selection = strput()
    term_cleaner()
    return selection

####### RENAME PLAYLIST #######

## Rename selection
def playlist_rename_select():
    print("""
___________________________________________________________\\/
Which playlist would you like to rename?                   |
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    selection = intput()
    term_cleaner()
    return selection

def playlist_new_name(playlist):
    print(f"""
___________________________________________________________/\\
You will be renaming) {playlist}
Please enter a new name.                                   \\/
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    new_name = strput()
    term_cleaner()
    return new_name

####### METADATA STUFF #######

## Write/Delete metadata
def tag_printer(tags, enter_msg):
    
    print("""___________________________________________________________\\/
▼ Valid tags ▼                                             /\\
""")
    for tag in tags.keys(): print(tag)

    print(f"""___________________________________________________________\\/
{enter_msg}
e.g) 3 album                                               _
                                                           |
0) Return                                                  |
___________________________________________________________|""")

    selection = strput()
    term_cleaner()
    return selection

def enter_new_metadata(data_choice, tag, curr_tag):
    print(f"""
__________________________________________________________/\\
{data_choice}
Selected tag) {tag}
Current tag data) {curr_tag}
                                                          \\/
0) Return                                                  |
___________________________________________________________|""")

    new_data = strput()
    term_cleaner()
    return new_data

####### SETTINGS #######

### Metadata main settings

def metadata_main_menu():
    print("""
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
Input: <playlist num> <setting>""")

    selection = strput()
    term_cleaner()
    return selection


### PLAYLIST SETTINGS
def main_settings_menu():
    print("""
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
___________________________________________________________|""")

    setting = intput()
    term_cleaner()
    return setting

### MAIN SETTINGS 
def main_settings(shuffl, ram, gap_state, video_state):
    print(f"""
___________________________________________________________
▼ Settings ▼                                               |
                                                           |
___________________________________________________________|
▼ Configs and Personalization ▼                            |
                                                           |
1) Toggle shuffle. (Currently: {shuffl}                /\\
2) Set maximum RAM usage when playing audio. (Currently: {ram}mB)
3) Enable/Disable gapless audio (Currently: {gap_state})
4) Enable/Disable video rendering (PC only, Currently: {video_state})
5) Website whitelist                                      \\/
___________________________________________________________|
▼ BnuuyPlayer main settings ▼                              |
                                                           |
6) Change Bnuuyplayer's database location                  |
7) BnuuyFolder/Playlist sub settings                       |
8) Song Metadata settings                                  |
0) Return.                                                 |
___________________________________________________________|""")

    select = intput()
    term_cleaner()
    return select 

def db_location_enter(curr_path):
    print(f"""
___________________________________________________________
Please enter a new path for BnuuyPlayer's database.       /\\
Current folder the database is in) {os.path.basename(curr_path)}
Note: Moving may take a while!                            \\/
___________________________________________________________|""")
    path = path_input()
    return path

#### MAX RAM SETTING SUB MENU 
def max_ram(ram_allocated):
    print(f"""
___________________________________________________________
Please enter any whole number above 1.                     /\\
Current max) {ram_allocated}mB
0) Return                                                  \\/
___________________________________________________________|""")

    selection = strput()
    term_cleaner()
    return selection


####### FIRST SETUP MENU #######

def first_setup_welcome():
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
___________________________________________________
|Welcome to BnuuyPlayer!                           |
|__________________________________________________|

To use BnuuyPlayer, there must first be a valid song folder/playlist.""")

####### MAIN MENU #######

def print_welcome():
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

def print_main(main_methods, no_hint):
    print("""___________________________________________________________
                                                          /\\""")
    for key, (name, _, _) in main_methods.items():
        print(f"{key}) {name}")
    print("__________________________________________________________\\/")
    if not no_hint:
        print("""▼ Extra commands ▼                                         |
                                                           | 
h/H) Extra information, use if you're lost.                |
t) Toggle this message off/on.                             |
___________________________________________________________|""")
    from . import __version__ as version
    print(f"""Version) {version}    /
_________________/""")

    choice = strput().lower()
    term_cleaner()
    return choice

def print_help(main_operations):
    print("""
___________________________________________________________
                                                          /\\""")
    for num, (name, hint, _) in main_operations.items():
        print(f"{num}) {name} \n Info: {hint}")

    print("___________________________________________________________\\/\n")
