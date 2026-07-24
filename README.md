bnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuybnuuy
# BnuuyPlayer guide

**No AI generated code was used**

**Wanna contribute? View [BnuuyPlayer's documentation](README_Files/README-Docs.md)**

**Wanna view features? View [BnuuyPlayer's featureset](README_Files/README-Features.md)**

**Wanna see the current roadmap? View [BnuuyPlayer's roadmap](README_Files/README-RoadMap.md)**

**Want to view the changelog? View [BnuuyPlayer's changelog](CHANGELOG.md)**

**Need help? view [help](#help), [the cheatsheet](#cheatsheet), or [general advice](#general-advice) :3**

**New to BnuuyPlayer? View below, this will aid you in installation and act as a guide.**

## Installation 

***NOTE: If you don't want to install MPV and use bnuuyplayer as a library manager/video downloader, then exclude MPV from the install command, it is the final package at the end of the command***

Linux (Debian, Ubuntu)
```bash
sudo apt update
sudo apt install python3 python3-pip mpv
``` 

Linux(Fedora)
```bash
sudo dnf update
sudo dnf install -y python3 python3-pip mpv
```

Linux (centOS)
```bash
# Exclude this if you don't want MPV 
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-$(rpm -E %rhel).noarch.rpm

# Exclude this if you don't want MPV
sudo dnf install -y https://download1.rpmfusion.org/free/el/rpmfusion-free-release-$(rpm -E %rhel).noarch.rpm

sudo dnf install -y python3 python3-pip mpv
```

Linux (Arch)
```bash
sudo pacman -Syu
sudo pacman -S python python-pip mpv
```

Windows
```bash
winget install Python.Python.3.13 shinchiro.mpv
```
MacOS
```bash
brew install python3 mpv
```
Android(termux)
```bash
pkg upgrade
pkg install python mpv
```

Python verification
```bash
python3 --version
```
(If this fails, lookup a guide on your specific OS)

### Installing bnuuyplayer itself, you have two methods

**▼ Note for both methods ▼**
**BnuuyPlayer will create a folder in your home directory on startup, this folder is it's database aswell as containing any folders you make using BnuuyPlayer.**
**This allows you to simply create a folder yourself and move the songs into that folder and allow BnuuyPlayer to search for them, or let BnuuyPlayer make the folder and you move the songs.**


#### 1: PyPI (most convenient)

```
pip install bnuuyplayer
```
Installed dependencies:
YT-DLP
Requests
Mutagen (optional, you can delete that one, although i recommend it since its only 400kb and opens up several features)

To run BnuuyPlayer via this method, enter
```bash
bnuy
```

#### 2: git clone

***This method will expose BnuuyPlayer's code, allowing you to modify or read it***
**IMPORTANT NOTE: This requires you have git installed!**

Installing:
```bash
cd path/to/your/dir
git clone https://github.com/whenth01/BnuuyPlayer.git
```
Dependencies:
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

***If you don't want to use --break-system-packages, please follow [this tutorial](https://www.geeksforgeeks.org/python/create-virtual-environment-using-venv-python/) on creating a venv by GeeksForGeeks***

To run BnuuyPlayer via this method, while your in it's directory enter
```
python3 -m BnuuyPlayerCode
```

## Cheatsheet, General advice and help.

### Cheatsheet

#### Create a new playlist/folder or add into a playlist.
  1. Return to Main Menu(if you arent already there)
  2. Settings
  3. Playlist sub settings
  
#### Play a song
1. Be at the main menu
2. Playlists (enter 1)
3. Select the playlist you want (or make one using the tutorial above, and repeat this)
4. Enter 1 to play all, or a special command

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
  If it is a direct link, create a feature request with the site you want added.

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
    

