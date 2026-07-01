# BnuuyPlayer guide

**No AI generated code was used.**

**Contributor? View [BnuuyPlayer's documentation](README-Docs.md)**

**Want to view features? View [BnuuyPlayer's featureset](README-Features.md)**

**Want to see the current roadmap? View [BnuuyPlayer's roadmap](README-RoadMap.md)**

**Want to view the changelog? View [BnuuyPlayer's changelog](README-ChangeLog.md)**

**New to BnuuyPlayer? View below, this will aid you in installation and act as a guide.**

## Installation 

***NOTE: If you don't want to install MPV and use bnuuyplayer as a library manager/video downloader, then exclude MPV from the install command, it is the final package at the end of the command***

Linux (Debian, Ubuntu)
```bash
sudo apt update
sudo apt install python3 python3-pip git mpv
``` 

Linux(Fedora)
```bash
sudo dnf update
sudo dnf install -y python3 python3-pip git mpv
```

Linux (centOS)
```bash
# Exclude this if you don't want MPV 
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-$(rpm -E %rhel).noarch.rpm

# Exclude this if you don't want MPV
sudo dnf install -y https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm

sudo dnf install -y python3 python3-pip git mpv
```

Linux (Arch)
```bash
sudo pacman -Syu
sudo pacman -S python python-pip git mpv
```

Windows
```bash
winget install Git.Git Python.Python.3.13 shinchiro.mpv
```
MacOS
```bash
brew install python3 git mpv
```
Android(termux)
```bash
pkg install python git mpv
```

Python verification
```bash
python3 --version
```
(If this fails, lookup a guide on your specific OS)

Dependency download;
```
pip install yt-dlp requests
```
Optional dependency:
```
pip install mutagen
```
Mutagen will unlock advanced by artist, album, and other advanced searching/playback.
This is recommended, as mutagen is only ~400 kB.
***NOTE: If the pip install fails, then add --break-system-packages to the install.***
E.g)
```bash
pip install yt-dlp requests --break-system-packages
```
***Note: What --break-system-packages does ▼***

Newer systems lock Python to stop pip from clashing with OS managed packages, normally pip blocks this with "externally managed environment"
It's safe here, as yt-dlp, requests and mutagen aren't packages the OS depends on

***If you don't want to use --break-system-packages, run ▼***

```bash
python3 -m venv venv && source venv/bin/activate
```

Now; go to a directory 
***(Do not use the home directory.)***
***(BnuuyPlayer will lagspike if you attempt to search for something if you do use the home directory.)***

Linux, Android(termux), MacOS
```bash
cd path/to/your/directory
```
Windows
```bash
cd path\to\your\directory
```

Finally, run)
```bash
git clone https://github.com/whenth01/BnuuyPlayer.git
```
and
```
python3 bnuuyplayerindev.py
```
***NOTE: This manual clone will be deprecated once BnuuyPlayer is moved into a PyPi package, after V1.1 you can safely delete git, and run BnuuyPlayer by running bnuy***


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
    
#### Advanced Search tagging
  Valid advanced searched tags
  title
  album
  artist

  To conduct an advanced search, all you must do is
  <the tag, e.g album> <your search query>
  And BnuuyPlayer returns you every song in the specified album.
  For example,
  album kick back
  That will show you every song from the album kick back by SPARKLEWOLF, and offer you a choice to
  1. Build a new BnuuyFolder with these songs
  2. Delete the songs.
  3. Append the tag into the filename
  4. Locate these songs
And more. (viewable in [[README-Features]]' mutagen section.)
    
#### URL Not working
  BnuuyPlayer only supports direct URLs, a mirror or shortlink will not work. 

#### Streamed playlists cant be browsed song by song
  This is currently a known limitation and may be fixed in V2.


### General advice

#### BnuuyFolders
  BnuuyFolders are not file system folders. They are collections of playlists, and do not affect filesystem nor interact with it.

#### 'Let BnuuyPlayer create a folder' 
  This only creates it within bnuuyplayer's directory.
    
#### 'Search for folder'
  This only searches within bnuuyplayer's directory, and not the whole device (To prevent a massive lagspike)

#### Deleting a sys folder
  If you choose to delete manually it will not affect BnuuyPlayer, as bnuuyplayer checks if the folder exists before interaction.
    

