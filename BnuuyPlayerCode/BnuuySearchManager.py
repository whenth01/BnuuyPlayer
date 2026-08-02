import os
import json
import shutil
import difflib
import subprocess
from . import BnuyNumUI as ui
from . import BnuuyFolderManager as bnuyfolder

try: import mutagen
except (ImportError, ModuleNotFoundError): pass

class BnuuySearcher:
    def __init__(self, bnuydata):
        self.data = bnuydata
        self.cache_path = os.path.join(self.data.bnuy_path, "BnuyCache.json")

    #### METADATA PRINT AND COLLECTION ####
    def metadata_helper(self, path):
        if not self.data.mutagen_installed:
            print("To access this, please run pip install mutagen")
            return
        metadata = {}

        invalid_ext = self.data.invalid_ext_set
        unsupported_ext = self.data.metadata_unsupported_ext

        for file in os.listdir(path):
            abs_path = os.path.join(path, file)

            key = max(metadata, default=0)+1
            if os.path.isdir(abs_path): 
                continue
            elif os.path.splitext(os.path.basename(file))[1].lower() in invalid_ext:
                continue
            elif os.path.splitext(os.path.basename(file))[1].lower() in unsupported_ext:
                continue

            try:
                data = mutagen.File(abs_path, easy=True)
            except (OSError, mutagen.MutagenError) as e:
                print(f"{file} failed to read!:(")
                print(e)
                continue
            if data is None: continue
            else: metadata[key] = data
            print(f"{key}) {os.path.basename(file)}")

        print("\nNote: if a song is missing, the file format is likely unsupported.")

        return metadata

    #### SEARCH LIBRARY ####

    def investibun_search(self):
        invalid_ext = self.data.invalid_ext_set
        lib_dict = self.data.lib_print(local_only=False, folder_only=False, suppress_print=True)
        keys = lib_dict.get("display_keys")
        while True:
            try:

                search_select = ui.investibun_main()

                if search_select == "0": return

                search_query = ui.investibun_query()
                
                if search_query == "0": return

                entries = {}
                songs = []
                playlists = []
                song_handler = False
                playlist_handler = False

                for key, tupl in self.data.song_paths.items():
                    if bnuyfolder.bnuuyfolder_check(tupl): continue

                    name, path, is_stream, _ = tupl

                    if search_select == "2": 
                        """Playlist route"""
                        disp_name = name

                        entries[len(entries)+1] = path, is_stream, name.lower(), key, disp_name
                        playlists.append(name.lower())
                        print(f"Checking) {name}..")
                        playlist_handler = True

                    elif search_select == "1":
                        """Songs route"""
                        if os.path.isdir(path):

                            compiler = []
                            for filename in os.listdir(path):
                                split = os.path.splitext(filename)
                                # filters out unwanted files
                                if split[1].lower() in invalid_ext: continue
                                # appends a lowercase filename to the list
                                compiler.append(split[0].lower())
                                print(f"Checking) {split[0]}..")

                            entries[key] = compiler
                            songs += compiler
                            song_handler = True

                        else: continue

                    else:
                        ui.general_exception()
                        break

                else:

                    if song_handler:
                        search = set(difflib.get_close_matches(search_query.lower(), songs, n=3, cutoff=0.5))
                    else:
                        search = set(difflib.get_close_matches(search_query.lower(), playlists, n=3, cutoff=0.5))

                    info = {
                        "search": search,
                        "disp_keys": keys,
                        "entries": entries,
                        "playlists": self.data.song_paths,
                        "playlist_handler": playlist_handler,
                    }

                    ui.basic_result_print(info)

            except ValueError:
                ui.general_exception()
                continue
    
    #### BULK HELPER'S FILE OPERATION ####
    def bulk_helper_helper(self, mode, path, dest_path, files):
        handled = False
        msg = ""
        if mode == "move":
            shutil.move(path, dest_path)
            handled = True
            msg = f"{os.path.basename(path)} was moved to {os.path.basename(dest_path)}"

        elif mode == "copy" and os.path.basename(path) not in files:
            shutil.copy(path, dest_path)
            handled = True
            msg = f"{os.path.basename(path)} was copied to {os.path.basename(dest_path)}"


        elif mode == "delete":
            os.remove(path)
            handled = True
            msg = f"{os.path.basename(path)} was deleted."

                
        elif mode == "play":
            player = [
                "mpv",
                path,
                f"--input-conf={self.data.keybind_dir}",
                "--profile=fast",
                "--no-video",
                "--cache",
                f"--demuxer-max-bytes={self.data.ram_allocated}m",
                ]
            try:
                subprocess.run(player, check=True)
            except subprocess.CalledProcessError as e:
                print(f"An error occurred!")
                print(e)
        return msg, handled


    #### METADATA COMPILER & BACKEND ####

    def bulk_helper(self, params, mode, dest_path):

        processed_files = 0

        for num, (metadata, path, key) in params.items():
            if not os.path.isdir(dest_path):
                ui.special_exception("Destination path was deleted, please select a new playlist!")
                break

            # This is a blacklist of files to prevent copy from overwriting same name files
            if mode == "copy": files = set(os.listdir(dest_path))
            # moving doesnt need it as it raises an error
            else: files = {}

            lrc_file = f"{os.path.basename(os.path.splitext(path)[0])}.lrc"
            lrc_path = os.path.join(os.path.dirname(path), lrc_file)

            moved_song = False
            if not os.path.isfile(path):
                print(f"{os.path.basename(path)} is missing or deleted, skipping..")
                continue

            try:
                msg, handled = self.bulk_helper_helper(mode, path, dest_path, files)
                if mode == "play": continue
                if handled:
                    print(msg)
                    processed_files += 1
                    moved_song = True
                else:
                    print(f"{os.path.basename(path)} failed to be copied due to another file with the same filename existing in the chosen playlist!")
                    moved_song = False

            except(shutil.Error, PermissionError, FileNotFoundError, OSError) as e:
                print("An error occurred while handling the song file!")
                print(e)
                print("Skipping song..")
                continue
            
            if os.path.isfile(lrc_path) and moved_song:
                try:
                    if mode == "play": continue
                    msg, handled = self.bulk_helper_helper(mode, lrc_path, dest_path, files)

                    if handled:
                        print(msg)
                        processed_files += 1
                    else:
                        # only copy route failing doesnt raise an exception
                        print(f"{lrc_file} failed to be copied due to another file with the same filename existing in the chosen playlist!")

                except(shutil.Error, PermissionError, FileNotFoundError, OSError) as e:
                    print("An error occurred while handling the lyric file!")
                    print(e)
                    print("Skipping lyric file..")
                    continue

        print("Finished handling the files!:3")
        return processed_files


    #### MULTIPLE FILE MOVER ####
    def bulk_mover(self, params):
        while True:
            try:
                res = self.data.lib_print(local_only=True)
                selection = ui.bulk_move_select()

                if selection == 0:
                    return
                
                keys = res.get("display_keys")
                selected_playlist = self.data.song_paths[keys[selection][0]]

                # is folder check
                if keys[selection][1]:
                    print("Can not select a folder, please select a playlist.")
                    continue
                # Stream check
                elif selected_playlist[2]: raise ValueError

                dest_path = selected_playlist[1]

                while True:
                    confirm = ui.bulk_move_confirm(params, selected_playlist[0])

                    if confirm == "0": break

                    elif confirm == "1":
                        amount_moved = self.bulk_helper(params, "move", dest_path)

                        print(f"Moved {amount_moved} files!:3")
                        return

                    else:
                        ui.general_exception()
                        continue

            except (ValueError, KeyError, IndexError):
                ui.special_exception("Please select a playlist, not a folder or streamed entry.")
                continue


    #### MULTIPLE FILE COPY ####

    def bulk_copy(self, params):
        copy_size_bytes = 0 
        for _, (_, path, _,) in params.items():
            if os.path.isfile(path):
                copy_size_bytes += os.path.getsize(path)

        copy_size_kb = copy_size_bytes / 1024
        copy_size_mb = copy_size_kb / 1024
        copy_size_gb = copy_size_mb / 1024

        while True:
            try:
                res = self.data.lib_print(local_only=True)

                dest_select = ui.bulk_copy_dest_menu()

                if dest_select == 0:
                    return

                keys = res.get("display_keys")

                selected_playlist = self.data.song_paths[keys[dest_select][0]]
                # folder check
                # keys hold a is folder value at index 1
                if keys[dest_select][1]:
                    ui.special_exception("Cannot select a folder :(, please select a playlist!")
                    continue

                # stream check
                elif selected_playlist[2]: raise ValueError

                confirm_loop = True
                while confirm_loop:
                    info = {
                        "playlist": self.data.song_paths[keys[dest_select][0]][0],
                        "params": params,
                        "mb": copy_size_mb,
                        "gb": copy_size_gb,
                    }

                    confirm = ui.bulk_copy_confirm(info)

                    if confirm == "1": pass

                    elif confirm == "0":
                        confirm_loop = False
                        break

                    else:
                        print("Invalid input, pick 1 or 0.")
                        continue

                
                    name, dest_path, _, _, = selected_playlist

                    amount_copied = self.bulk_helper(params, "copy", dest_path)

                    print(f"Copied {amount_copied} files!:3")
                    return


            except (ValueError, KeyError, IndexError):
                ui.general_exception("Please select a playlist")
                continue

    #### METADATA BASED BULK DELETE ####

    def bulk_delete(self, params):
        while True:
            try:
                confirm = ui.bulk_del_confirm(params)


                if confirm == 1:
                    # spoofing the dest path to make it fit in
                    amount_deleted = self.bulk_helper(params, "delete", self.data.bnuy_path)
                    print(f"Deleted {amount_deleted} files.")
                    return 

                elif confirm == 0:
                    return

                else: raise ValueError

            except ValueError:
                ui.general_exception("Select 0 or 1.")
                continue

    #### METADATA BASED PLAYBACK ####

    def metadata_player(self, params):
        self.bulk_helper(params, "play", self.data.bnuy_path)

    #### LOAD CACHE ####

    def metadata_cache_loader(self):
        try:
            with open(self.cache_path, "r") as f:
                cached_metadata = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            cached_metadata = "no data"

        if cached_metadata == "no data": return None

        self.cache_verifier(cached_metadata)
        return cached_metadata

    #### WRITE TO CACHE ####

    def metadata_cache_saver(self, cached_metadata):
        try:
            with open(self.cache_path, "w") as f:
                json.dump(cached_metadata, f, indent=2)
        except OSError:
            print("An error occurred while trying to save to cache. The next search may take longer!")

    #### VERIFY CACHE INTEGRITY ####

    def cache_verifier(self, cached_metadata):
        removal_list = []
        for file, _ in cached_metadata.items():
            if not os.path.isfile(file):
                removal_list.append(file)

        for file in removal_list:
            del cached_metadata[file]

    #### Mutagen advanced search ####

    def advanced_investibunny(self):
        if self.data.mutagen_installed is False:
            print("Mutagen is uninstalled. to access this run) pip install mutagen")
            return

        bulk_methods = {
        "1": self.bulk_mover,
        "2": self.bulk_copy,
        "3": self.bulk_delete,
        "4": self.metadata_player
        }

        # Generally unsupported extensions
        invalid_ext = self.data.invalid_ext_set
        # Extensions that are unsupported by Mutagen
        unsupported_ext = self.data.metadata_unsupported_ext
        # valid search tags
        tags = {
            "artist": "artist",
            "title": "title",
            "album": "album",
            "genre": "genre",
            }

        while True:
            try:
                cached_metadata = self.metadata_cache_loader()

                if cached_metadata is None:
                    use_cache = False
                    cached_metadata = {}
                else: use_cache = True


                selection = ui.advanced_select_query()

                values = selection.split()
                if values[0] == "0": return

                elif len(values) < 2: raise ValueError

                else:
                    tag = tags.get(values[0])

                    if tag is None: raise ValueError

                    # reconstructs the string 
                    # 0 is the tag (as seen above)
                    query = " ".join(values[1:])
                    results = {}
                    # this starts by searching playlists in self.data.song_paths 
                    # for their metadata
                    for num, tupl in self.data.song_paths.items():
                        if bnuyfolder.bnuuyfolder_check(tupl): continue
                        
                        name, path, is_stream, _ = tupl
                        
                        if not is_stream:
                            # then begins looking through local songs..
                            if not os.path.isdir(path):
                                print(f"Encountered an invalid playlist) {name}\nIgnoring...")
                                continue
                            for file in os.listdir(path):
                                # filters invalid songs and files
                                if os.path.splitext(file)[1].lower() in invalid_ext: 
                                    continue
                                full_file = os.path.join(path, file)
                                # collects the metadata
                                mod_time = os.path.getmtime(full_file)

                                if use_cache:
                                    file_data = cached_metadata.get(f"{full_file}")
                                    try:
                                        if file_data is None:
                                            got_cached_data = False

                                        elif int(mod_time) == int(file_data.get("mtime")):
                                            metadata = file_data.get("metadata")
                                            got_cached_data = True

                                        else: got_cached_data = False
                                    except TypeError:
                                        del cached_metadata[full_file]
                                        got_cached_data = False

                                else: got_cached_data = False

                                try:
                                    if got_cached_data is False:
                                        metadata = mutagen.File(full_file, easy=True)

                                        # this is done because mutagen objects arent JSON serializable :(
                                        stuff = {}
                                        if metadata is not None:
                                            for tag_name, data in metadata.items():
                                                stuff[tag_name] = data

                                        cached_metadata[full_file] = {
                                                "mtime": mod_time,
                                                "metadata": stuff,
                                                }

                                        if os.path.splitext(file)[1].lower() in unsupported_ext:
                                            print(f"{file} is unsupported.")
                                            continue

                                except mutagen.MutagenError as e:
                                    print("An error occurred! ▼")
                                    print(e)
                                    print("Ignoring the file..")
                                    continue

                                if metadata is None or len(metadata) == 0:
                                    print(f"{file} had no metadata.")
                                    continue

                                # pulls the selected tag from the metadara
                                value = metadata.get(tag)

                                if value is None:
                                    print(f"{file} did not have {tag} in its metadata :(")
                                    continue

                                for data in value:
                                    # fuzzy search through the results
                                    check = difflib.SequenceMatcher(None, data.lower(), query.lower()).ratio()
                                    if check < 0.5: 
                                          print(f"{file} did not match.")
                                          continue
                                    # if its a match > 50%, it saves the result
                                    else: 
                                        results[len(results)+1] = (metadata, full_file, num)
                                        break

                    self.metadata_cache_saver(cached_metadata)
                    while True:
                        if len(results) == 0:
                            print("\nNo results found:(")
                            break

                        else:

                            data = self.data.lib_print(local_only=False, folder_only=False, suppress_print=True)
                            keys = data.get("display_keys")

                            ui.advanced_result_print(results, self.data.song_paths, keys)
                            choice = ui.advanced_result_selection()

                            funct = bulk_methods.get(choice)
                            if choice == "0": break

                            elif funct is None: 
                                ui.general_exception("Select a number between 0-4")
                                continue

                            else: 
                                ui.term_cleaner()
                                funct(results)
                                break

            except ValueError:
                ui.general_exception("Read BnuuyPlayer's README.md help section.")
                continue

            except IndexError:
                ui.general_exception()
                continue
