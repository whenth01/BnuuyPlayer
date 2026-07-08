import os
from . import BnuyNumUI as ui
from . import BnuuyFileManager as file_io
# escape from loops
class Escape(Exception): pass

#### FOLDER CHECK ####

def bnuuyfolder_check(tupl):
    valid_sentinels = {
        "Folder",
        "liked_songs",
    }
    # tupl[0] is the sentinel
    if len(tupl) == 2 and tupl[0] in valid_sentinels: return True
    # an IndexError would occur with only empty folders
    try: is_stream = tupl[2]
    except IndexError: return False


    if isinstance(is_stream, bool): return False

    if tupl[0] in valid_sentinels: return True
    else: return False

class BnuuyFolder():
    def __init__(self, bnuydata):
        self.valid_sentinels = {
           "Folder",
           "liked_songs",
       }

        self.data = bnuydata
        self.BnuyFileManager = file_io.LoadAndRecov(self.data)

    #### DEFAULT FOLDER CREATOR ####

    # Creates a default internal folder if they dont exist
    def default_bnuuyfolders(self):
        liked_exists = False
        next_key = max(self.data.song_paths, default=0)+1

        for num, tupl in self.data.song_paths.items():
            if bnuuyfolder_check(tupl) and tupl[0] == "liked_songs":
                liked_exists = True

        if liked_exists is not True:
            self.data.song_paths[next_key] = ["liked_songs", "Liked songs",]

    #### BNUUYFOLDER METHODS ####
    def create_bnuuyfolder(self):
        while True:
            try:
                ui.term_cleaner()
                folder_name = ui.new_bnuuyfolder_name()

                if folder_name == "0": break

                # This is used to identify folders 
                # This works as reg playlists always are a tuple in the 0 index 
                # while the 0 index in folders are a str to differentiate 
                folder_id = "Folder"
                tmp_list = []
                tmp_list.append(folder_id)
                tmp_list.append(folder_name)
                next_key = max(self.data.song_paths, default=0)+1
                self.data.song_paths[next_key] = tmp_list

                while True:

                    self.BnuyFileManager.saver()
                    choice = ui.new_bnuuyfolder_made()

                    match choice:
                        case "1": break
                        case "0":  raise Escape
                        case _: 
                            ui.general_exception()
                            continue

            except Escape:
                break


    #### FOLDER MANAGER ####

    def bnuuyfolder_manager(self, tupl):
        while True:
            disp_keys = {}
            playlists = {}
            try:

                ui.term_cleaner()
                name = tupl[1]

                if tupl[0] == "liked_songs":
                    songs = self.liked_manager(tupl)
                    return songs

                print(f"""
___________________________________________________________/\\ 
▼ Playlists in {name} ▼""")

                # Folders contain keys of playlists rather then full tuples.
                for num in tupl[2:]:
                    disp_keys[len(disp_keys)+1] = num

                for key, og_key in disp_keys.items():
                    name, path, is_stream, function = self.data.song_paths[og_key]
                    if is_stream:
                        print(f"{key}) {name} (Online stream)")
                    else: 
                        print(f"{key}) {name}")
                    playlists[key] = path

                # If the folder is empty
                if len(tupl) == 2: print("No playlists in the folder.")


                choice = ui.open_top_bottom_menu()


                if choice == "0": return None
                elif choice == "a": return playlists

                else:
                    choice = int(choice)

                    res = {
                         "selected": self.data.song_paths[disp_keys[choice]],
                         "key": disp_keys[choice],
                          }
                    return res


            except (ValueError, KeyError):
                ui.general_exception()
                continue


    #### BnuuyFolder adder ####

    def bnuuyfolder_adder(self):
        while True:
            try:
                res = self.data.lib_print()
                folder_choice = ui.select_playlist_folder()
                if folder_choice == "0": break
                elif folder_choice.lower() == "h": 
                    ui.bnuuyfolder_add_help_text()
                    continue

                local = res.get("local_dict")
                stream = res.get("stream_dict")
                folders = res.get("folder_dict")
                display_keys = res.get("display_keys")

                # This is done to preserve the original keys, which full (in the passed dict) doesnt have.
                full = local | stream | folders

                keys = folder_choice.split()

                if len(keys) != 2:
                    ui.general_exception("Please enter h for the help message :3")
                    continue

                # Converts back into ints.
                int_keys = [int(key) for key in keys]

                checked_keys = set()

                try: playlist = full.get(display_keys[int_keys[0]][0])
                except KeyError: playlist = None
                
                try: folder = full.get(display_keys[int_keys[1]][0])
                except KeyError: folder = None

                if playlist is None: 
                    ui.special_exception("No playlist found.")
                    continue

                elif folder is None: 
                    ui.special_exception("No folder found.")
                    continue

                elif not bnuuyfolder_check(folder): 
                    ui.special_exception("Selected folder was a playlist, invalid input")
                    continue

                elif bnuuyfolder_check(playlist):
                    ui.special_exception("Selected playlist was a folder, invalid input")
                    continue
                
                elif folder[0] == "liked_songs":
                    ui.special_exception("Can not add the try into liked songs via this method.\nPlease go to playlist picker's song menu.")
                    continue

                for key in folder[2:]:
                    checked_keys.add(key)

                if display_keys[int_keys[0]][0] in checked_keys:
                    ui.special_exception("Folder already has that playlist.")
                    continue

                confirm = ui.bnuuyfolder_confirm_add(playlist[0], folder[1])

                if confirm == "1": 

                    # This writes the key from self.song_paths rather then a copy
                    # appends it into the actual folder
                    folder.append(display_keys[int_keys[0]][0])
                    
                    # overwrites the old folder entry into the main library
                    self.data.song_paths[display_keys[int_keys[1]][0]] = folder
                    self.BnuyFileManager.saver()

                    print("\nSuccess!\n")
                elif confirm == "0":
                    continue
                else: raise ValueError


            except (ValueError, IndexError, KeyError):
                ui.general_exception()
                continue

    #### BnuuyFolder del ####

    def bnuuyfolder_del(self):
        while True:
            try:
                res = self.data.lib_print(local_only=False, folder_only=True)
                folder_dict = res.get("folder_dict")
                keys = res.get("display_keys")

                del_choice = ui.delete_bnuuyfolder_selection()
                if del_choice == 0: break

                match = folder_dict.get(keys[del_choice][0])

                if match is None:
                    ui.general_exception("No matches found.")
                    continue

                sentinel = match[0]

                if sentinel == "liked_songs":
                    ui.special_exception("Can not delete the liked songs folder.")
                    continue

                else: 
                    name = match[1]

                    confirm = ui.delete_bnuuyfolder_confirm(name)

                    if confirm == 1:
                        self.data.internal_delete(keys[del_choice][0])
                        print("Successfully deleted.\n")
                        continue 
                    elif confirm == 0: 
                        print("Canceled.\n")
                        continue
                    else:
                        raise ValueError

            except (ValueError, KeyError):
                ui.general_exception()
                continue


    #### PLAYLIST FROM FOLDER DEL ####

    def del_from_bnuuyfolder(self):
        while True:
            try:
                res = self.data.lib_print(local_only=False, folder_only=True)

                folder_dict = res.get("folder_dict")
                library = res.get("full_dict")
                keys = res.get("display_keys")

                folder_choice = ui.del_select_bnuuyfolder()

                if folder_choice == 0: break
                else:
                    folder = library[keys[folder_choice][0]]
                    if not bnuuyfolder_check(folder):
                        raise ValueError

                    if folder[0] == "liked_songs": 
                        self.liked_remover(folder)
                        continue

                    res = self.bnuuyfolder_manager(folder)
                    if res is not None:
                        del_playlist = res.get("selected")
                        key = res.get("key")

                        if del_playlist is None:
                            ui.special_exception("This choice is unselectable from this area(del from bnuuyfolder)!")
                            continue

                    else: del_playlist = None

                    # Backing out to callerroute
                    if del_playlist is None: return

                    confirm = ui.del_confirm(del_playlist[0], folder[1])

                    if confirm == 1:
                        folder.remove(key)
                        self.BnuyFileManager.saver()
                        print("Success! X3\n")

                    elif confirm == 0: break

                    else: raise ValueError

            except (ValueError, KeyError):
                ui.general_exception()
                continue

    #### EDIT BNUUYFOLDER NAME ####

    def rename_bnuuyfolder(self):
        while True:
            try:
                res = self.data.lib_print(local_only=False, folder_only=True)
                folders = res.get("folder_dict")
                keys = res.get("display_keys")

                edit_choice = ui.bnuuyfolder_rename_select()

                if edit_choice == 0: break 

                selected = folders.get(keys[edit_choice][0])

                if selected is None:
                    ui.special_exception("Not a valid folder.")
                    continue

                else:
                    selected = folders.get(keys[edit_choice][0])
                    name = selected[1]
                    ui.term_cleaner()
                    rename = ui.bnuuyfolder_rename(name)

                    if rename == "0": break 
                    else: 
                        selected[1] = rename
                        self.data.song_paths[keys[edit_choice][0]] = selected
                        self.BnuyFileManager.saver()
                        print("Success!")


            except (ValueError, KeyError):
                ui.general_exception()
                continue

    ###### LIKED SONGS BNUUYFOLDER ######

    #### LIKED FOLDER MANAGER ####

    def liked_manager(self, liked):
        songs = {}
        db_changed = False
        # We start at index 1 because liked is split by [2:]
        # and the for loop immediately adds 1
        curr_index = 1
        # Note; liked manager does not handle printing. Callers of it do
        print("""
___________________________________________________________/\\
▼ Liked songs ▼""")

        for path in liked[2:]:
            curr_index += 1
            if not os.path.isfile(path):
                db_changed = True
                found = False
                """Song search"""
                for root, dirs, files in os.walk(self.data.bnuy_path):

                    for file in files:
                        if os.path.basename(path) == file:
                            path = os.path.join(root, file)
                            liked[curr_index] = path
                            found = True

                            break 

                    if found: 
                        songs[len(songs)+1] = path
                        break

                if found is False: 
                    print("A liked song disappeared; was it deleted or moved out?")
                    print(f"Missing song) {os.path.basename(os.path.splitext(path)[0])}")
                    liked.remove(path)
                    curr_index -= 1
                    continue

            else: songs[len(songs)+1] = path

        if db_changed:
            self.BnuyFileManager.saver()

        return songs

    #### LIKED SONG REMOVE ####

    def liked_remover(self, folder):
        while True:
            try:
                songs, no_songs, choice = ui.liked_songs_remover_print(folder)

                if choice == 0: break 
                else:
                    if choice not in range(1, len(songs)+1) or no_songs:
                        ui.general_exception("No song at that number was found!")
                        continue

                    selected_path = songs[choice]

                    # This does a manual search because liked songs have no keys
                    for path in folder[2:]:
                        if path == selected_path:
                            folder.remove(selected_path)

                            print(f"Successfully unliked {os.path.basename(os.path.splitext(path)[0])}! :3")
                            self.BnuyFileManager.saver()
                            break
                    continue

            except (ValueError, KeyError):
                ui.general_exception()
                continue
