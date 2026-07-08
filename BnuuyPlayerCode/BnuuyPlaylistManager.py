import os
import requests
from shutil import rmtree
from . import BnuyNumUI as ui
from . import BnuuyFileManager as file_io
from . import BnuuyFolderManager as folder_management

# This is used in the YT_Dlp method if the user enters a wrong url
class BadURL(Exception): pass
# Escape out of loops
class Escape(Exception): pass


class PlaylistAdding():
    def __init__(self, bnuydata):
        self.data = bnuydata
        self.BnuyFileManager = file_io.LoadAndRecov(self.data)
        self.BnuyFolders = self.data.BnuyFolder


    #### ADD PLAYLIST ####
    
    def add_playlist(self):
        while True:
            try:
                choice = ui.adder_menu()

                if choice == 0: return # Return to last menu

                funct = self.data.adders[choice]()
                break

            except (ValueError, KeyError):
                ui.general_exception()
                continue


    #### PLAYLIST/PATH ADDER ####
    def path_adder(self):
        is_stream = False
        while True:
            try:
                path_input = ui.path_input()
                if path_input == "0":
                    break

                """Folder validator"""
                is_playlist_path = os.path.isdir(path_input)

                # Validates that the folder exists
                if not is_playlist_path:
                    print("\nDirectory doesn't exist, or you made a typo.")
                    continue

                # If the folder exists, keep going
                else:
                    while True:
                        name_choice = ui.path_playlist_name()
                        if name_choice == "1":
                            print("Enter the display name.")
                            playlist_name = ui.strput()
                            break

                        # Assigns the folder the base name
                        elif name_choice == "2":
                            playlist_name = os.path.basename(path_input)
                            break

                        else:
                            ui.general_exception()
                            continue

                    # Save to song paths, write to disk, flip initializer if false
                    next_key = max(self.data.song_paths, default=0)+1 

                    self.data.song_paths[next_key] = (playlist_name, path_input, is_stream, self.data.BnuyDJ.audio_funct)

                    self.BnuyFileManager.saver()
                    ui.term_cleaner()
                    print("Playlist successfully added!")

                    self.data.initializer()

                    path_input = ui.path_final_menu()

                if path_input == "0": break

                elif path_input == "1": continue

                else: raise ValueError

            except ValueError:
                ui.general_exception()
                continue

    #### ADD/CREATE FOLDER ####
    # note: this is separate from bnuuyplayer's internal folders
    # and creates physical folders in current directory
    def folder_maker(self):
        is_stream = False
        while True:
            try:

                confirm = ui.allow_folder_creation()

                if confirm == "1":
                    folder_name = ui.new_folder_name()

                    folder_path = os.path.join(self.data.bnuy_path, folder_name)
                    os.makedirs(folder_path)

                    next_key = max(self.data.song_paths, default=0)+1
                    self.data.song_paths[next_key] = (folder_name, folder_path, is_stream, self.data.BnuyDJ.audio_funct)

                    self.BnuyFileManager.saver()
                    ui.success_print(folder_path)

                    self.data.initializer()
                    break

                elif confirm == "0": break

                else: raise ValueError

            except FileExistsError:
                ui.special_exception("\nFolder or file already exists.")
                continue

            except OSError:
                ui.bad_folder_names()
                continue

            except ValueError:
                ui.general_exception()
                continue

    #### DIRECTORY SEARCHER ####

    def folder_searcher(self):
        while True:
            is_stream = False
            countr = 0
            song_path_len = max(self.data.song_paths, default=0)+1

            name = ui.main_folder_search(self.data.bnuy_path)

            if name == "0":
                break

            results = {}
            res_len = len(results)

            # Goes through and searches for directories in the current dir.
            try:
                for root, dirs, _ in os.walk(self.data.bnuy_path):
                    if name in dirs:
                        res_len += 1

                        combined = os.path.join(root, name)
                        results[res_len] = (name, combined, is_stream, self.data.BnuyDJ.audio_funct)


                # If multiple folders are found, print every root and key 
                # and ask the user for one of them, or all
                if len(results) > 1:
                    print("\nMultiple folders found!")

                    while True:
                        for key, (name, root, _, _) in results.items():
                            print(f"{key}) found at: {root}")
                        choice = ui.multi_folder_found()
                        try:
                            choice = int(choice)

                            if choice > len(results) or choice < 0:
                                ui.general_exception()
                                continue

                            else: break
                        except ValueError:
                            if choice == "a": break
                            else: raise ValueError

                    # writes every found entry into playlists
                    if choice == "a":
                        for key, (name, root, _, _) in results.items():
                            song_path_len += 1
                            self.data.song_paths[song_path_len] = (name, root, is_stream, self.data.BnuyDJ.audio_funct)
                            combined = root

                    # write chosen one into playlists
                    elif choice in range(1, len(results)+1):
                        song_path_len += 1
                        name, root, _, _ = results[int(choice)]
                        self.data.song_paths[song_path_len] = (name, root, is_stream, self.data.BnuyDJ.audio_funct)
                        combined = root

                    else: raise ValueError

                # if only 1 is found, write immediately
                elif len(results) == 1:
                    song_path_len += 1
                    _, combined, _, _ = results[1]
                    self.data.song_paths[song_path_len] = results[1]

                else:
                    raise Escape

                choice = ui.folder_success(combined)
                self.BnuyFileManager.saver()
                self.data.initializer()

                if choice == 0: break
                
                elif choice == 1: continue
                
                else: raise ValueError

            except Escape:
                ui.special_exception("Folder not found.")
                continue

            except ValueError:
                ui.general_exception()
                continue


    #### YOUTUBE DOWNLOADER/STREAMER ####

    def yt_adder(self):
        # Used to filter correct and false video extensions
        vid_ext = {"mp4",
                   "webm",
                   "mkv",
                   "avi",
                   "mov",
                   "dv",
                   "mpg",
                   "mpeg",
                   "m4v",
                   "ts",
                   "mxf",
                   "ogv",
                   "rm",
                   "swf",
                   "flv",
                   "gxf",
                   "asf",
                   "wmv",
                   "3gp",
                   "3g2",
                   "f4v",
                   "nuv",
                   "roq",
                   "ivf",
                  }

        while True:
            try:
                song_path_len = max(self.data.song_paths, default=0)+1
                choice = ui.stream_or_dl()

                url_inp = ":3"
                while True:

                    # if the choice ISNT 0; it runs this
                    if choice != 0:
                        try:

                            url_inp = ui.url_input()
                            # returns to last menu
                            if url_inp == "0":
                                break
                            # filters through to find matching domain 
                            tmp_url = [url for url in self.data.valid_domains if url in url_inp]

                            # if no matches found, raise badurl
                            if len(tmp_url) == 0:
                                raise BadURL


                            url_valid = requests.get(url_inp, timeout=10)
                            # Checks url's validity
                            url_valid.raise_for_status()

                            """Invalid/wrong URL handler"""
                        except BadURL:
                            ui.print_site_whitelist(self.data.valid_domains)
                       
                            """Internet error"""
                        except requests.exceptions.ConnectionError as e:
                            ui.special_exception(f"No internet, DNS error or refused connection, full error below. \n\n{e}")
                            continue

                            """General error"""
                        except(
                            requests.exceptions.MissingSchema,
                            requests.exceptions.InvalidSchema,
                            requests.exceptions.InvalidURL,
                            requests.exceptions.InvalidHeader,
                        ) as e:
                            ui.special_exception(f"Invalid URL, or an issue occurred regarding the URL occurred. Full error may be below  \n{e}")
                            continue

                            """Timeout"""
                        except requests.exceptions.Timeout:
                            ui.special_exception("Timeout error, URL took too long to respond.")

                            """HTTPError"""
                        except requests.exceptions.HTTPError as e:
                            ui.special_exception(f"An unknown error occurred, error message from the server ▼ \n\n{e}")

                        # if no error occurs, this runs as the url is likely valid 
                        # this breaks out of the inner loop to let the code continue
                        else:
                            break

                    elif choice == 0:
                        break

                    else:
                        ui.general_exception()
                        continue

                if url_inp == "0": continue

                if choice == 1:
                    dl_location = ui.download_selection()
                    match dl_location:
                        case 1:

                            while True:

                                # prints every playlist and writes to tmp_dict

                                print_results = self.data.lib_print(local_only=True)

                                countr = print_results.get("local_countr")
                                local_dict = print_results.get("local_dict")
                                keys = print_results.get("display_keys")

                                # if no playlists this runs
                                if len(local_dict) < 1:
                                    print("\nNo playlists currently available.")
                                try:
                                    dl_dest = ui.pick_playlist_dl()
                                    # selects the playlist from tmp via dict unpacking
                                    if dl_dest != 0:
                                        (name, path, _, _) = local_dict[keys[dl_dest][0]]
                                        break

                                    elif dl_dest == 0:
                                        return

                                    else:
                                        ui.general_exception()
                                        continue

                                except KeyError:
                                    ui.general_exception("Bad number entered!")
                                    continue

                        case 2:

                            while True:
                                folder_name = ui.pick_new_folder_name()
                                # combines bnuy path and folder name then creates
                                try:
                                    path = os.path.join(self.data.bnuy_path, folder_name)
                                    os.makedirs(path)
                                    break

                                except FileExistsError:
                                    ui.special_exception("Folder already exists.")
                                    continue

                                except OSError as e:
                                    ui.special_exception(f"OSError occurred! Error msg: {e}")
                                    continue

                            disp_name = ui.disp_name_select()
                            # if user selects 0, use folder name
                            # else use disp name
                            name = None
                            try:
                                os.rmdir(path)
                            except (OSError, FileNotFoundError, PermissionError): 
                                pass 
                            if disp_name == "1": 
                                name = folder_name

                            elif disp_name == "0": 
                                try:
                                    os.rmdir(path)
                                except (FileNotFoundError, PermissionError, OSError):
                                    pass 
                                continue
                            else: name = disp_name

                            is_stream = False
                            next_key = max(self.data.song_paths, default=0)+1
                            self.data.song_paths[next_key] = (
                                f"{name}",
                                path,
                                is_stream,
                                self.data.BnuyDJ.audio_funct,
                             )

                        # return to last menu
                        case 0:
                            continue

                        case _:
                            raise ValueError

                    while True:
                        ext = ui.file_extension_select()


                        yt_opts = {
                                "outtmpl": f"{path}/%(title)s.%(ext)s",
                                "format": "bestaudio/best",
                                "progress_hooks": [self.data.yt_hook],
                                "ignoreerrors": "only_download",
                                "no_warnings": True,
                                "postprocessors": [{
                                    "key":"FFmpegMetadata", "add_metadata": True,
                                    }]
                                }
                        yt_processor = {
                            "postprocessors": [{
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": ext,},
                                {
                                "key":"FFmpegMetadata", "add_metadata": True,
                                }],
                            }

                        if "." in ext:
                            print("Invalid ext, do not include a dot!")
                            continue

                        # deletes file sys folder to prevent orphaned folders
                        elif ext == "0":
                            if dl_location == 2:
                                try: os.rmdir(path)
                                except OSError: pass
                                del self.data.song_paths[next_key]

                            break

                        # if its a audio format; use postprocessors, else dont
                        elif ext not in vid_ext:
                            yt_opts.update(yt_processor)

                        else:
                            yt_opts["format"] = f"best[ext={ext}]"

                        # start downloading, yt opts for flags
                        try:
                            import yt_dlp
                            with yt_dlp.YoutubeDL(yt_opts) as ydl:
                                ydl.download(url_inp)

                        except (yt_dlp.utils.DownloadError, yt_dlp.utils.PostProcessingError) as e:
                            if "unsupported" in str(e).lower():
                                print("Unsupported URL, or a invalid URL was inputted.")
                            else:
                                print(
                                f"Download failed, error message; {repr(e)}\n\nPlease report the error to the github page if its not a connection error."
                                )
                            continue

                        # if no errors occur, print this
                        print("\nSuccessfully downloaded!\n")

                        self.data.initializer()
                        self.BnuyFileManager.saver()

                        break

                # stream path
                elif choice == 2:

                    if url_inp == "0": break


                    name_choice = ui.streamed_playlist_name()

                    if name_choice == "0": break

                    is_stream = True

                    # writes to song paths
                    self.data.song_paths[song_path_len] = (
                        name_choice,
                        url_inp,
                        is_stream,
                        self.data.BnuyDJ.audio_funct,
                    )

                    self.BnuyFileManager.saver()
                    print("Successfully added!")
                    self.data.initializer()

                elif choice == 0: break

                else: raise ValueError

            except (ValueError, KeyError):
                ui.general_exception()
                continue





class PlaylistManagement():
    def __init__(self, bnuydata):
        self.data = bnuydata
        self.adders = self.data.BnuyPlaylistAdd
        self.BnuyFolders = self.data.BnuyFolder

    #### DELETE PLAYLIST FROM DISK ####

    def del_playlist_from_disk(self):
        while True:
            try:

                results = self.data.lib_print(local_only=True)
                # assigns values
                local_paths = results.get("local_dict")
                countr = results.get("local_countr")
                keys = results.get("display_keys")
                # lib print sets local back to False as a side effect

                del_choice = ui.delete_playlist_selection()

                if del_choice == 0: return

                """Delete processer"""
                # find the path, remember name for later
                delname, path, _, _ = local_paths[keys[del_choice][0]]
                while True:
                    final_confirm = ui.delete_confirm(delname)

                    if final_confirm == "0": 
                        print("Canceled.")
                        break

                    elif final_confirm == "1":

                        """Recursive delete"""
                        try:
                            rmtree(path)
                        except (OSError, PermissionError) as e:
                            ui.special_exception(f"An error occurred while deleting!) {e}")
                            continue
                            

                        """Library updater"""
                        # Reindexes and deletes selected playlist
                        self.data.internal_delete(keys[del_choice][0])
                        print("Successfully deleted!")
                        break

                    else:
                        ui.general_exception()
                        continue

            except ValueError:
                ui.general_exception()
                continue

            except KeyError:
                ui.general_exception("Only playlists are selectable!\n")
                continue

    #### DELETE PLAYLIST ####

    def del_playlist(self):
        while True:
            try:
                res = self.data.lib_print()
                keys = res.get("display_keys")

                del_choice = ui.remove_playlist()

                if del_choice == 0: return

                else:
                    playlist = self.data.song_paths[keys[del_choice][0]]

                    if folder_management.bnuuyfolder_check(playlist):
                        ui.special_exception("Can not delete folders here, please select a playlist!")
                        continue

                    confirm = ui.confirm_remove(playlist[0])

                    if confirm == 1:
                        self.data.internal_delete(keys[del_choice][0])
                    elif confirm == 0: continue
                    else: raise ValueError

                    print("Successfully removed!")
                    continue

            except (ValueError, KeyError):
                ui.general_exception()
                continue
    
        #### EDIT PLAYLIST NAME ####

    def edit_playlist_name(self):
        while True:
            try:
                results = self.data.lib_print(local_only=True)
                countr = results.get("full_countr")
                local_paths = results.get("full_dict")
                keys = results.get("display_keys")

                rename_choice = ui.playlist_rename_select()
                if rename_choice == 0: return

                if countr > 0 and rename_choice in range(1,len(keys)+1):
                    selected_key = keys[rename_choice][0]

                    playlist = self.data.song_paths[selected_key]

                    if folder_management.bnuuyfolder_check(playlist):
                        ui.special_exception("Can not rename folders here!")
                        continue

                    new_name = ui.playlist_new_name(playlist[0])

                    if new_name == "0": continue 

                    playlist = list(playlist)
                    playlist[0] = new_name
                    self.data.song_paths[selected_key] = tuple(playlist)
                    self.data.BnuyFileManager.saver()

                    print("Successfully renamed. :3")
                    continue

                else: raise ValueError
                                    

            except ValueError:
                ui.general_exception()
                continue


    #### PLAYLIST SETTINGS #### 
    def playlist_settings(self):
        settings = {
                #### FOLDER METHKDS ####
                1: self.BnuyFolders.create_bnuuyfolder,
                2: self.BnuyFolders.bnuuyfolder_adder,
                3: self.BnuyFolders.bnuuyfolder_del,
                4: self.BnuyFolders.del_from_bnuuyfolder,
                5: self.BnuyFolders.rename_bnuuyfolder,

                #### PLAYLIST METHODS ####
                6: self.del_playlist,
                7: self.del_playlist_from_disk,
                8: self.adders.add_playlist,
                9: self.edit_playlist_name,
                }
        while True:
            try:
                choice = ui.main_settings_menu()

                ####rExtra commands ####
                if choice == 0: 
                    """Back"""
                    break

                elif choice in range(1, len(settings)+1):
                    settings[choice]()
                    continue

                else: raise ValueError 

            except (ValueError, KeyError):
                ui.general_exception()
                continue
