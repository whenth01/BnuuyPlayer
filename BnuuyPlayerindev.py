import os, subprocess, sys, shutil, yt_dlp, json



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
  print(f"""\nKeybindings;
q) Quit
Q) Quit, but saves position
l) Loop current song
m) Mute
p / space ) Pause
P) show progress
i) Info
< / >) Go backward/forward in the playlist
[ / ]) -10% and +10% playback speed
{{ / }}) Half/double playback speed
Backspace) Reset playback speed to normal
9 / 0) Vol +2 / -2
+ / -) skip 5s / back 5s
s / b) skip 30s / back 30s
G / F) Increase / decrease subtitle size
""")

def adder_menu():
  choice = int(input(f"""1) Specify the path to your own folder.

2) Allow BnuuyPlayer to make a folder automatically.

3) Allow BnuuyPlayer to search for a specified folder.
(BnuuyPlayer can only search within the folder it's in.)

4) Youtube download/stream.
(Downloading may take up a chunk of storage.)
(Streaming may introduce buffering.)

5) Skip.
(Warning, This is intended for testing, unexpected behavior may occur.)


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
      for num, tupl in song_paths.items():
        if len(tupl) == 3:
          (name, _, _) = tupl
          print(f"{num}) {name}")
          countr += 1 
        else:
          (name, _, _, is_stream) = tupl
          print(f"{num} {name} (Online stream.)")
          countr += 1


      choice = int(input("""0) back

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
".it", ".caf", ".ape", ".wma"}
        for song in os.listdir(path):
          filename, ext = os.path.splitext(song)

          if ext not in invalid_ext:
            filepath = os.path.join(path, song)
            countr += 1
            print(f"{countr}) {filename}")
            tmp_song[countr] = filepath
        is_stream = False

      except(ValueError):
          print("Warn: Individual song picking is unsupported for streaming due to technical limitations.")
          (name, path, function, is_stream) = song_paths[choice]


      tmp_boolean = True
      while tmp_boolean:
        if is_stream: break
      
        choice = int(input("""\n1) Play the whole playlist
2) Play one song
3) Back

>>> """))
        term_cleaner()

        if choice == 1: break

        elif choice == 2:
          choice = int(input("""Enter the num of the song you'd like

>>> """))
          path = tmp_song[choice]
          break

        elif choice == 3: raise FileNotFoundError

        else: raise ValueError

      if not shuffl[0]:
        player = ["mpv", path, f"--input-conf={directory}", "--profile=fast", "--no-video"]
      else:
        player = ["mpv", path, f"--input-conf={directory}", "--profile=fast", "--no-video", "--shuffle"]

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
    for num, tupl in song_paths.items():
      if len(tupl) != 3:
        name, combined = tupl
        tmp_handler[num] = (name, combined, audio_funct)
      else:
        name, combined, is_stream = tupl
        tmp_handler[num] = (name, combined, audio_funct, is_stream)

    song_paths = tmp_handler
    res = {i: v for i, v in enumerate(song_paths.values(),start=1)}
    song_paths.clear()
    song_paths.update(res)



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
      print("""Hint: Valid file paths are:

MacOS: /users/<your_username>/...
Linux: /home/<your_username>/...
Android: /storage/emulated/0/...
Windows: C:\\users\\<your_username>\\...

These are how your device sees your folders/files.
A folder named "Synth" on android in the Home dir would be 
/storage/emulated/0/synth\n""")
      path_input = input("""B) Back
Please input the path to the folder.
>>> """)
      is_playlist_path = os.path.isdir(path_input)

      if path_input == "B":
        break

      if not is_playlist_path:
        term_cleaner()
        print("\nDirectory dosen't exist, or you made a typo.")
        continue

      else:
        term_cleaner()
        while True:
          name_choice = input("""Would you like to use the folder name, or create a display name?
1) Create a display name(Only affects how Bnuuyplayer shows you the playlist!)
2) Use the folder name

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
      
        path_input = input("""Would you like to add one more or continue?
c) Continue to BnuuyPlayer.
a) Add one more path.
>>> """).lower()

      if path_input == "c": break
      elif path_input == "a": continue
      else: raise ValueError

    except(ValueError):
      print("Invalid input.\n")
      continue

#### ADD/CREATE FOLDER ####

def folder_maker(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path):
  term_cleaner()
  while True:
    try:
      folder_name = input("""Continue to let BnuuyPlayer to make a folder.
1) Continue
2) Back
>>> """)
      if folder_name == "1":
        term_cleaner()
        folder_name = input("""What would you like to name the playlist?
>>> """)

        song_path = os.path.join(bnuy_path, folder_name)
        os.makedirs(song_path)

        num = len(song_paths)+1

        song_paths[num] = (folder_name, song_path, audio_funct)
        saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
        term_cleaner()
        print(f"""Successfully created.
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
      print(f"""\nUnknown Error. You likely use an invalid character/name for the folder name.

Invalid character/name list:
Windows: 
< > : - " / \\ | ? *

CON, PRN, AUX, 
NUL COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9 
LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9

0-31 (ASCII control characters)

Names also cannot end in a dot or space.

Linux:
0 (NULL byte)
/
. (special name referring to current directory) 
.. (special name referring to parent directory)

macOS:
:
/

Android:
< > : - " / \\ | ? *

\\n
0-31 (ASCII control characters)""")
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
    name = input("""Please enter the folder name you'd like BnuuyPlayer find.
B) return

>>> """)

    if name == "B": break

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
          choice = int(input("""Which one is correct? If all are, enter "0"
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
        song_paths[song_path_len] = (name, combined, audio_funct)

      else:
        raise UnboundLocalError

      term_cleaner()
      choice = int(input(f"""Successfully found at {combined}\n
1) Return to BnuuyPlayer
2) Add another folder.
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
      choice = int(input("""1) Download the video/playlist(may take up significant storage, but plays offline and no buffering)
2) Stream the video/playlist(buffering and online only)
0) Back

>>> """))

      if choice != 0: 
        term_cleaner()
        url_inp = input("""Enter the url 

>>> """)
      if choice == 1:
        term_cleaner()
        choice = int(input("""Where would you like to download the file(s)?

1) Put the song(s) in a already existing playlist. (Local playlists only.)

2) Allow BnuuyPlayer to make a folder.

3) Return.

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
            choice = int(input("""Pick a playlist.

>>> """))
            (_, path, _) = song_paths[choice]
          

          case 2:
            term_cleaner()
            folder_name = input("""What would you like to name the folder?

>>> """)
            path = os.path.join(bnuy_path, folder_name)
            os.makedirs(path)
            disp_name = input("""Would you like a display name for the folder?
0) No, continue.

>>> """)
            if disp_name == "0": 
              song_paths[len(song_paths)+1] = folder_name, path, audio_funct
            else:
              song_paths[len(song_paths)+1] = disp_name, path, audio_funct

          case 3: continue

          case _: raise ValueError

        term_cleaner()
        ext = input("""Enter the file extension you'd like.
__________________________
▼ Recommended choices ▼   |
                          |
mp4                       |
mp3                       |
m4a                       |
__________________________|
▼ Unsupported extensions ▼|
                          |
midi/mid                  |
mod, xm, s3m, it          |
caf                       |
ape                       |
wma                       |
__________________________|
Do not include a dot when entering the file extension!

>>> """)
        print("Successfully completed operations, song(s) being downloaded now..")


        yt_opts = {"outtmpl": f"{path}/%(title)s.%(ext)s",
                   "format": "bestaudio/best",
                   "postprocessors": [{
                       "key": "FFmpegExtractAudio",
                       "preferredcodec": ext,
                       }]
                  }
        term_cleaner()
        with yt_dlp.YoutubeDL(yt_opts) as ydl:
          ydl.download(url_inp)

        print("\nSuccessfully downloaded!\n")

        initializer(initialized)
        saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)

      elif choice == 2:
        initializer(initialized)
        name_choice = input("Enter a name: ")
        is_stream = True
        song_paths[song_path_len] = (name_choice, url_inp, audio_funct, is_stream)
        saver(song_paths, initialized, shuffl, no_hint, bulk_save, hist_path)
        print("Successfully added!")
        initializer(initialized)


      elif choice == 0:
        break

      else: raise ValueError
 

    except(ValueError):
      print("\nInvalid input.")
      continue


#### ADDER DICT ####

adders = {
1: path_adder,
2: folder_maker,
3: song_searcher,
4: yt_adder,
5: "Skip."
}


#### SETTINGS / NON-MUSIC ####
def settings(shuffl, song_paths, adders, bulk_save, initialized, no_hint, hist_path):
  while True:
    try:
      choice = int(input("""\n1) Toggle shuffle. (This is saved between sessions!)
2) Delete a playlist.
3) Add a playlist.
0) Return.

WIP
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

        for num, tupl in song_paths.items():
          if len(tupl) == 3:
            (name, _, _,) = tupl
            print(f"{num}) {name}")
          else:
            (name, _, _, _,) = tupl 
            print(f"{num}) {name} (Online streaming.)")

        del_choice = int(input("""Which would you like to delete? 
(This only deletes the playlist from BnuuyPlayer!)
0) return

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
        if choice == 5:
          continue

        funct = adders[choice]
        funct(song_paths, initialized, bnuy_path, bulk_save, no_hint, hist_path)

    except(ValueError, KeyError):
      term_cleaner()
      print("Invalid input.\n")
      

#### OPERATIONS ####

main_operations = {
"1": ("Playlists", "Your library, this is where your songs and playlists live.", audio_funct),
"2": ("Keybinds", "Music player keybinds.", binding_menu),
"3": ("Settings", "Your settings, you can toggle shuffle, add/remove songs, and do more here.", settings),
"e": ("Exit", "Closes the audio player", exity)
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
        elif choice == 5:
          initializer(initialized)
          break

        else: raise ValueError
        

      except(ValueError):
        term_cleaner()
        print("\nInvalid Input.")
        continue
          
        


#### MAIN MENU ####

def main_menu(main_operations, song_paths, initialized, no_hint, hist_path, bulk_save, shuffl):
    term_cleaner()
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
⠀⠀⠀⠀⠈⠉⠙⠛⠻⠿⠛⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
 ________________________________________________________________________
|Welcome back to BnuuyPlayer!                                            |
|________________________________________________________________________|
⠀⠀⠀⠀
""")

    while True:
      try:
        for key, (name, _, _) in main_operations.items():
          print(f"{key}) {name}")

        if not no_hint[0]:
          print("Hint: enter h / H for extra information, or 0 to toggle this message.")
        choice = input(">>> ").lower()

        if choice == "h":
          term_cleaner()
          for num, (name, hint, _) in main_operations.items():
            print(f"""{num}) {name}
Info: {hint}
""")
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
        if name == "Settings":
          function(shuffl, song_paths, adders, bulk_save, initialized, no_hint, hist_path)
        elif name == "Keybinds":
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
