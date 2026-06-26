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

- [x] The code permanently rearranges the folder's files(how??)
- [x] The music stops playing after a song ends(in a whole playlist)
**(Both of these are either out of bnuuyplayer's control, or unknown how they occur)**

### FEATURES

- Fully implemented search function(added song search and playlist search)

