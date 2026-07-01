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
- [x] The music stops playing after a song ends(in a whole playlist)
**(Both of these are either out of bnuuyplayer's control, or unknown how they occur)**

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

