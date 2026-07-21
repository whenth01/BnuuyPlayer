# ChangeLog

## V0.2 BETA

### BUGFIXES AND POLISHING
- [x] Add a clearer seperation between file system folders and internal BnuuyFolders
**Solved**
- [x] Change the installation tutorial for linux(fedora, and base off actual documentation, report if still wrong)
**Solved**
- [x] Patch the 0 (return) in playlist picker(currently a hard crash on the thread)
**Solved**
- [x] Add a os.listdir and a os.path.isdir check for playlists (to prevent playing an empty or invalid playlist)
**Solved**
- [x] Change the wording of add a new playlist in sub settings
**Solved**
- [x] Investigate YT-Dlp downloader menu being buggy
*It tries to download every playlist regardless if the format is bad*
*It dosent break the loop after selecting a good playlist key*
**Solved.**
Note: The return's behaviour is currently too destructive, will be reworked soon.

- [ ] The code permanently rearranges the folder's files(how??)
**left unsolved because no deletion occurs, just strange unreproducible behavior**
- [x] The music stops playing after a song ends(in a whole playlist)
**(Both of these are either out of bnuuyplayer's control, or unknown how they occur, but havent been reproduced)**

### FEATURES

- Fully implemented search function(added song search and playlist search)

## V0.3 BETA
### MAIN
- [x] Bug fixes
- [x] Added mutagen support, finished bulk move and bulk copy and advanced search
- [x] Fixed gaps in some menus 
- [x] Made MPV an optional install
- [x] Added write to metadata
- [x] Added delete to metadata
- [x] Added other stuff(idk I.forgot:(, just read features)

### OTHER
- Bulk renaming playlists was deferred(due to it already existing manually, this may be reintegrated in v1.1-v2)

### V0.31
- [x] Added playback capability in advanced search
- [x] Several bugfixes

## V0.4 BETA
### FEATURES
- [x] Added a toggle that allows the user to allocate a custom amount of RAM to MPV
- [x] Added a toggle that allows BnuuyPlayer to play video (PC only, this'll do nothing on Android)
- [x] Added gapless audio toggle
- [x] Added time playing statistic
- [x] Made the border of the first time welcome text smaller
- [x] Added adding songs/playlists to main menu

## V1.0.1 RELEASE!!!!
### BACKEND
- Moved all UI into BnuyNumUI.py
- Moved all folder related features into BnuuyFolderManager.py
- Moved audio playback and playlist picking to BnuuyAudio.py
- Moved playlist stuff into BnuuyPlaylistManager.py
- Moved file stuff and saving into BnuuyFileManager.py
- Moved except hook into ```__init__.py```

### FEATURES
- Added play all playlists in BnuuyFolder
- All names can now be liked_songs, as it used to block the user to prevent a collision with a default BnuuyFolder

### OTHER
- BnuuyPlayer has been uploaded to PyPI, removing manual install(except for binaries)!!:3

## V1.0.2
### BUG FIXES
- BnuuyPlayer now creates a folder in your home directory, using that as it's container for it's database (aswell as any folders you generate using BnuuyPlayer).
**This was done as installing via pip polluted the python package dir, and made folders/jsons inaccsssible.**

### PLANNED FEATURES
- The bug fix will be expanded upon soon to allow you to decide where BnuuyPlayer's database lives.

## V1.0.3
### BUG FIXES
- Fixed a bug where attempting to play an individual song/stream a playlist would crash the code

- Fixed a bug where
1. Playlist picker would open a BnuuyFolder(user chosen)
2. Detects a dead playlist in the BnuuyFolder
3. Sends the wrong key, reusing the key for the BnuuyFolder as the bad playlist's key, which would either delete the wrong playlist or fail :(
- Added onto the previous bug, a failsafe in bnuuyfolder's manager where it catches the error and deletes the bad playlist itself
(my library was affected by this bug. QwQ)

- Other stuff(i forgor)


### FEATURES
- Added [planned feature](#planned-features) from V1.0.2
- Added how to play a song to readme.md's help section