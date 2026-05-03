import os, subprocess, sys, yt_dlp, json



no_hint = [False]
initialized = [False]
shuffl = [False, "placeholder"]

bnuy_path = os.path.dirname(__file__)

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
l cycle-values loop-file inf no
"""

try: 
  directory = os.path.join(bnuy_path, "bnuybinds.conf")
  is_conf = os.path.exists(directory)
  if not is_conf:
    raise FileNotFoundError 

except(FileNotFoundError):
  with open(directory, "w") as f:
    f.write(bnuybinds)

def initializer(initialized):
  if not initialized[0]:
    initialized[0] = True

#### TERMINAL CLEANER ####

def term_cleaner():
  os.system('cls' if os.name == 'nt' else 'clear')

#### KEYBINDED MENU ####

def binding_menu():
  term_cleaner()
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
                                                           |
2) Allow BnuuyPlayer to make a folder automatically.       |
                                                           |
3) Allow BnuuyPlayer to search for a specified folder.     |
(BnuuyPlayer can only search within the folder it's in.)   |
                                                           |
4) Youtube download/stream.                                |
(Downloading may take up a chunk of storage.)              |
(Streaming may introduce buffering.)                       |
                                                           |
0) Skip/back.                                              |
___________________________________________________________|

>>> """))
  term_cleaner()
  return choice

############# MAIN #############

#### MUSIC PLAYER ####

def audio_funct(directory):
  term_cleaner()

  result = playlist_picker(song_paths, bnuy_path, shuffl, directory)
  try:
    _, _, _, path, player = result
    binding_menu()
    print("")
    subprocess.run(player)
  except(ValueError, KeyError):
    pass


#### PLAYLIST PICKER ####
def playlist_picker(song_paths, bnuy_path, shuffl, directory):

  while True:
    try:

      countr = 0
      term_cleaner()
      print("__________________________________________________________/\\")
      for num, tupl in song_paths.items():
        if len(tupl) == 3:
          (name, _, _) = tupl
          print(f"{num}) {name}")
          countr += 1 
        else:
          (name, _, _, is_stream) = tupl
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
        (name, path, function) = song_paths[choice]
        invalid_ext = {
".midi", ".mid", ".mod", ".xm", ".s3m",
".it", ".wma"}
        for song in os.listdir(path):
          filename, ext = os.path.splitext(song)

          if ext not in invalid_ext:
            filepath = os.path.join(path, song)
            countr += 1
            print(f"{countr}) {filename}")
            tmp_song[countr] = filepath
        is_stream = False

      except(ValueError):
          print("Warning: Individual song picking is unsupported for streaming due to technical limitations.")
          (name, path, function, is_stream) = song_paths[choice]


      tmp_boolean = True
      while tmp_boolean:
        if is_stream: break
      
        if len(os.listdir(path)) < 1:
          term_cleaner()
          print("\nPlaylist is empty.\n")

        choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Play the whole playlist                                 |
2) Play one song                                           |
3) Back                                                    |
___________________________________________________________|

>>> """))

        if choice == 1: break

        elif choice == 2:
          choice = int(input("""
___________________________________________________________
Enter the num of the song you'd like                       |
___________________________________________________________|

>>> """))
          path = tmp_song[choice]
          break

        elif choice == 3: raise FileNotFoundError

        else: raise ValueError

      if not shuffl[0]:
        player = ["mpv", path, f"--input-conf={directory}", "--profile=fast", "--no-video"]
      else:
        player = ["mpv", path, f"--input-conf={directory}", "--profile=fast", "--no-video", "--shuffle"]

      term_cleaner()

      return choice, name, function, path, player

    except(KeyError, ValueError):
      print("Invalid input.")
      continue

    except(FileNotFoundError): continue



#### PLAYLISTS ####

song_paths = {}
bulk_save = {}

#### PERSISTENT HIST CREATOR ####

try:

  hist_path = os.path.join(bnuy_path, "BnuyPlayerHist.json")
  with open(hist_path, 'r') as f:
    bulk_save = json.load(f)

    song_paths = bulk_save["0"]
    initialized = bulk_save["1"]
    no_hint = bulk_save["2"]
    shuffl = bulk_save["3"]
 
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
        print(f"""Found invalid save path, was the JSON edited/corrupted?
Found {invalid_countr} invalid save paths.
Corrupted/edited path) {tupl}""")

        err_paths[len(err_paths)+1] = tupl

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
      del_dict.clear() # Delete invalid/corrupted song paths.

    res = {i: v for i, v in enumerate(song_paths.values(),start=1)}
    song_paths.clear()
    song_paths.update(res) # Reindexes song path keys.




except(FileNotFoundError,AttributeError,KeyError,json.JSONDecodeError):
  with open(hist_path, "w") as f:
    json.dump(bulk_save, f, indent=2) 

############# MAIN FOLDER/SETUP AREA #############


#### HISTORY ADDER ####

def saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path):
  tmp_handler = {}


  for num, tupl in song_paths.items():
    check = len(tupl)
    if check == 3:
      name, combined, audio_funct = tupl
      tmp_handler[num] = (name, combined)
    else:
      name, combined, audio_funct, is_stream = tupl
      tmp_handler[num] = (name, combined, is_stream)


  song_paths = tmp_handler

  bulk_save = {}

  bulk_save[0] = song_paths
  bulk_save[1] = initialized
  bulk_save[2] = no_hint
  bulk_save[3] = shuffl

  with open(hist_path, 'w') as f:
    json.dump(bulk_save, f, indent=2)


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

        song_path_len = len(song_paths)+1
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

      if path_input == "1": break
      elif path_input == "2": continue
      else: raise ValueError

    except(ValueError):
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

        num = len(song_paths)+1

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

    except(FileExistsError):
      print("\nFolder already exists.")
      continue

    except(OSError):
      print(f"""
___________________________________________________________
Unknown Error. You likely use an invalid character/name.   |
___________________________________________________________|
                                                           |
Invalid character/name list                                |
                                                           |
___________________________________________________________|
Windows:                                                   |
< > : - " / \\ | ? *                                       |
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
< > : - " / \\ | ? *                                       |
\\n                                                        |
0-31 (ASCII control characters)                            |
                                                           |
___________________________________________________________|""")
      continue
    
    except(ValueError):
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

    if name == "0": break

    results = {}
    res_len = len(results)

    try:
      for root, dirs, files in os.walk(bnuy_path): 
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
          else: break

        if choice == 0:
          for key, (name, root, _) in results.items():
            song_path_len += 1
            song_paths[song_path_len] = (name, root, audio_funct)
            combined = root

        else:
          song_path_len += 1
          (name, root, _) = results[choice]
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
___________________________________________________________
Successfully found at {combined}!                          |
___________________________________________________________|
▼ Extra commands ▼                                         |
                                                           | 
1) Return to BnuuyPlayer                                   |
2) Add another folder.                                     |
___________________________________________________________|

>>> """))
      saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
      initializer(initialized)


      if choice == 1: break
      elif choice == 2: continue
      else:
        term_cleaner()
        raise ValueError

    except(UnboundLocalError):
      print("\nFolder not found.")
      continue
    except(ValueError):
      print("\nInvalid input.")
      continue

#### YOUTUBE DOWNLOADER/STREAMER ####

def yt_adder(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path):
  while True:
    try:
      song_path_len = len(song_paths)+1
      choice = int(input("""
___________________________________________________________
▼ Commands ▼                                               |
                                                           |
1) Download the video/playlist(may take alot of storage)   |
2) Stream the video/playlist(Online only)                  |
0) Back                                                    |
___________________________________________________________|

>>> """))

      if choice != 0: 
        term_cleaner()
        url_inp = input("""
___________________________________________________________
Enter a url                                                | 
___________________________________________________________|

>>> """)
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
            for num, tupl in song_paths.items():
              if len(tupl) == 3:
                (name, _, _) = tupl
                countr += 1
                print(f"{countr}) {name}")
            if len(song_paths) < 1:
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
            if choice != 0: (_, path, _) = song_paths[choice]

            else: continue
          

          case 2:
            term_cleaner()
            folder_name = input("""
___________________________________________________________
What would you like to name the folder?                    |
___________________________________________________________|

>>> """)
            path = os.path.join(bnuy_path, folder_name)
            os.makedirs(path)
            term_cleaner()
            disp_name = input("""
___________________________________________________________
Would you like a display name for the folder?              |
                                                           |
0) No, continue.                                           |
___________________________________________________________|

>>> """)
            if disp_name == "0": 
              song_paths[len(song_paths)+1] = folder_name, path, audio_funct
            else:
              song_paths[len(song_paths)+1] = disp_name, path, audio_funct

          case 0: continue

          case _: raise ValueError

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
"mp4", "webm", "mkv", "avi", "mov", "dv",
"mpg", "mpeg", "m4v", "ts", "mxf", "ogv",
"rm", "swf", "flv", "gxf", "asf", "wmv",
"3gp", "3g2", "f4v", "nuv", "roq", "ivf"
}
          if "." in ext:
            print("Invalid ext, do not include a dot!")
            continue
          elif ext == "0":break

          elif ext not in vid_ext:
            yt_opts = {"outtmpl": f"{path}/%(title)s.%(ext)s",
                       "format": "bestaudio/best",
                       "postprocessors": [{
                           "key": "FFmpegExtractAudio",
                           "preferredcodec": ext,
                        }]
                      }

          else:
            yt_opts = {"outtmpl": f"{path}/%(title)s.%(ext)s",
                       "format": f"bestvideo[ext={ext}]+bestaudio/best"}

          term_cleaner()
          try:
            with yt_dlp.YoutubeDL(yt_opts) as ydl:
              ydl.download(url_inp)
          except yt_dlp.utils.DownloadError as e:
            if "unsupported" in str(e).lower():
              print("Unsupported URL, or a invalid URL was inputted.")
            else:
              print(f"Download failed, error message; {repr(e)}\n\nPlease report the error.")
            continue

          print("\nSuccessfully downloaded!\n")

          initializer(initialized)
          saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
          break

      elif choice == 2:
        initializer(initialized)
        name_choice = input("""
___________________________________________________________
Enter a name                                               |
___________________________________________________________|

>>> """)
        is_stream = True
        song_paths[song_path_len] = (name_choice, url_inp, audio_funct, is_stream)
        saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
        print("Successfully added!")
        initializer(initialized)


      elif choice == 0:
        break

      else: raise ValueError
 

    except(ValueError, KeyError):
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
        print("___________________________________________________________")
        for num, tupl in song_paths.items():
          if len(tupl) == 3:
            (name, _, _,) = tupl
            print(f"{num}) {name}                                                  | ")
          else:
            (name, _, _, _,) = tupl 
            print(f"{num}) {name} (Online streaming.)                              |")

        del_choice = int(input("""
___________________________________________________________
                                                           |
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

          res = {i: v for i, v in enumerate(song_paths.values(),start=1)}
          song_paths.clear()
          song_paths.update(res)
 
          print(f"Successfully deleted!\n")
          saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)

        continue

      elif choice == 3:
        choice = adder_menu()
        if choice == 0:
          continue

        funct = adders[choice]
        funct(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path)

    except(ValueError, KeyError):
      term_cleaner()
      print("Invalid input.\n")
      

#### OPERATIONS ####

main_operations = {
"1": ("Playlists", "Your library, your songs/playlists are here.         ", audio_funct),

"2": ("Keybinds ", "Music player keybinds.                               ", binding_menu),

"3": ("Settings ", "Your settings, this is where important functions are.", settings),

"e": ("Exit     ", "Closes BnuuyPlayer.                                  ", exity)
}

#### INITIAL SETUP ####

def file_setup(initialized, song_paths, adders):
  term_cleaner()
  if not initialized[0]:
    while True:
      try:
        print(f"""
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
          funct(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path)
          break
        elif choice == 0:
          initializer(initialized)
          break

        else: raise ValueError
        

      except(ValueError):
        term_cleaner()
        print("\nInvalid Input.")
        continue
          
        


#### MAIN MENU ####

def main_menu(main_operations, song_paths, initialized, no_hint, hist_path, bulk_save, shuffl):

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
          print("""
▼ Extra commands ▼                                         |
                                                           | 
h/H) Extra information, use if you're lost.                |
0) Toggle this message off/on.                             |
___________________________________________________________|""")
        choice = input(">>> ").lower()

        if choice == "h":
          term_cleaner()
          print("___________________________________________________________")
          for num, (name, hint, _) in main_operations.items():
            print(f"""{num}) {name}                                               |
Info: {hint}|
                                                           |""")
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
        (name, _, function) = main_operations[choice]
        if choice == "3":
          function(shuffl, song_paths, adders, bulk_save, initialized, no_hint, hist_path)
        elif choice == "2":
          function()
        else: function(directory)

      except(KeyError):
        print("\nInvalid input.")
        continue

while True:
  if not initialized[0]:
    file_setup(initialized, song_paths, adders)
  else:
    main_menu(main_operations, song_paths, initialized, no_hint, hist_path, bulk_save, shuffl)
