## FEATURES

### Core playback
- [x] MPV/YT-DLP Integration
- [x] Full MPV keybinds(customizable)
- [x] Persistent shuffle toggle

## Library
### Playlists
- [x] Rename playlist
- [x] Delete playlist from disk/internally
- [x] Move/Add individual songs to playlists
- [x] Per song commands(delete, play, move, copy, like)
- [x] Rename playlists
- [x] Delete playlists (From disk or internally)
- [x] Playlist adding(Online download and stream, local files/folders both fully supported)
- [x] Streamed and local playlists(stored and displayed seperately)
- [x] Search for songs and playlists

### Mutagen
***This is currently being developed!***
- [x] Mutagen(optional dependency)
- [ ] Advanced Search
- [ ] Compile every song with a specified tag into a BnuuyFolder
- [ ] Write new tags
- [ ] Include author in the song title(in playlist picker)
- [ ] Download lyrics from preexisting songs(if metadata tags are available)

### Folders (internal)
- [x] Internal folder system(Seperate from OS file sys folders for sorting playlists)
- [x] Create/rename/delete folders
- [x] Auto created default folder(Liked songs folder, has special behavior allowing for individual songs to be played that the user likes.)
- [x] Like/Unlike songs(auto updates liked songs folder)

### Adding music
- [x] Add by absolute filepath, with custom or auto generated display name.
- [x] Create a new empty file system folder from BnuuyPlayer
- [x] Auto search the current directory BnuuyPlayer is in for a specified file sys folder
- [x] Download/stream online.
    *Supported sites: Youtube, soundcloud, bandcamp, vimeo, tiktok, reddit, instagram, facebook, dailymotion, mixcloud, audiomack*

### Lyrics
- [x] Auto download synced/plain lyrics from lrclib.net(only during download/mutagen auto download)
    *Stored as a .lrc next to the downloaded file*
    
## Other

### UI
*Both are optional; but the user must pick atleast 1.*
- [x] Numeric UI
    *Learning curve; but quicker when fully learnt.*
- [ ] Curses UI 
    *Navigable visual TUI, similar to cmus*

### Data handling and integrity
- [x]  Triple redundant system(3 jsons, 2 backup 1 main)
- [x] Auto recovery/rebuild system if main is partially corrupted
- [x] Data cannot be corrupted by midwrite crashes(os.replace via a tmp file)
- [x] Invalid/deleted filepaths are auto deleted from the database on startup.

### Settings & Stats
- [x] Persistent shuffle
- [ ] Timed used, time playing stats
- [x] Toggleable main menu hint
- [ ] Maximum ram usage by MPV(minimum of 1)
- [x] First run setup guide

### EasterEggs
- [ ] Hints are in settings.

## Nerd Area
- [ ] Full code splitup(into seperate files)
```
__init__.py
bnuycore.py
bnuyplayer.py
bnuyfolders.py
bnuyplaylists.py
bnuyadders.py
bnuyfilehandler.py
bnuynumUI.py
bnuycurseUI.py
```
- [ ] Code optimizations and streamlining(lib print rework, if/else chains turned into dictionary dispatches, removing anti patterns, etc)