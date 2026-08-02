# BnuuyPlayer NerdInfo

**note: this barely covers alot the code as i dont expect this to be used**
## Database

### Write to Database
```python

class Example()
    def __init__(self, bnuydata):
        self.data = bnuydata # bnuydata is the self object passed from the core file, which already instantiated everything
 
   def some_method(self)
       self.data.BnuyFileManager.saver()
 
```
### Delete from database
```python
# (assuming you transported the core object from BnuuyPlayerCore, in a similar method as shown above)
self.data.internal_delete(playlist_key)
```

### How BnuuyPlayer handles JSON and it's database.

***NOTE: BnuuyPlayer uses a translation layer for the user's display vs internal keys***
This is essentially
```python
self.song_paths = {
1: (name, pointer, is_stream, audio_funct)
3: (name, pointer, is_stream, audio_funct)
5: ["Folder", folder_name, 1, 3]
}
```
And the translation layer does:
```python
display_nums = {
1: (1, is_folder) # Is folder false
2: (3, is_folder) # Is folder false
3: (5, is_folder) # Is folder true
}
```
Which is storing the self.song_paths key next to a cleanly ordered one.
***Note: These are rebuilt each time self.lib_print is called, this is a known rough edge that will be remade in v1.1***

#### Flat playlists
  BnuuyPlayer handles playlists as tuples structured as
  ```python
  (name, pointer, is_stream, audio_funct)
  ```
  Name is a user inputted display name, or a auto generated one using the directory's path. (Note: these do not affect code flow and act entirely as a display name for the user.)

  The pointer is either a filepath or a URL, the code skips having to do a live request to differentiate by using is_stream(a boolean, True when its a URL and False when not.)
    
  audio_funct is what does the subprocess call to MPV to begin playing, playlist_picker and lib_print handle compiling the necessary information for audio_funct

#### Folders
  BnuuyPlayer stores folders as a list of pointers to the playlists rather then a full tuple copy to stay storage efficient.
  Essentially
  ```python
  self.song_paths = {
  1: (name, pointer, is_stream, audio_funct)
  2: (name, pointer, is_stream, audio_funct)
  3: ["Folder", folder_name, 2, 1]
  }
  ```
  Folders simply append the key of a selected playlist into themself, which the code can then reference as which playlist to open.
  **Note: "Folder" must always be in a BnuuyFolder entry as the first entry, this is what differentiates them from playlists**
  
>!:3!<