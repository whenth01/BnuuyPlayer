# BnuuyPlayer guide

**Contributor? View [BnuuyPlayer's documentation](README-Docs)**

**Want to view features? View [BnuuyPlayer's featureset](README-Features)**

**Want to see the current roadmap? View [BnuuyPlayer's roadmap](README-RoadMap)**

**New to BnuuyPlayer? View below, this will aid you in installation and act as a guide.**

## Installation 
Linux
```bash
apt install mpv python git
``` 
Windows
```bash
winget install mpv python git
```
MacOS
```bash
brew install mpv python git
```
Android(termux)
```bash
pkg install mpv python git
```

Dependency download;
```
pip install yt-dlp requests
```

Now; go to a directory ***(Do not use the home directory.)***
Linux, Android(termux)
```bash
cd path/to/your/directory
```
MacOS
```bash
cd /Users/<your-username>/path/to/your/directory
```
Windows
```bash
cd c:\Users\<your-username>\path\to\your\directory
```

Finally;
```bash
git clone https://github.com/whenth01/BnuuyPlayer.git
```
***NOTE: This manual clone will be deprecated once BnuuyPlayer is moved into a PyPi package, after V5.1 you can safely delete git.***


## Cheatsheet, General advice and help.

### Cheatsheet

#### Create a new playlist/folder or add into a playlist.
    1. Return to Main Menu(if you arent already there)
    2. Settings
    3. Playlist sub settings

### Help

#### BnuuyFolders not hiding playlists
    This is currently intentional; BnuuyFolders are an extra layer of organization for the user.
    True containment will come in V2.

#### URL Not working
    BnuuyPlayer only supports direct URLs, a mirror or shortlink will work. 

#### Streamed playlists cant be browsed song by song
    This is currently a known limitation and may be fixed in V2.


### General advice

#### 'Let BnuuyPlayer create a folder' 
    This only creates it within bnuuyplayer's directory.
    
#### 'Search for folder'
    This only searches within bnuuyplayer's directory, and not the whole device (To prevent a massive lagspike)

#### Deleting a sys folder
    If you choose to delete manually it will not affect BnuuyPlayer, as bnuuyplayer checks if the folder exists before interaction.
    

