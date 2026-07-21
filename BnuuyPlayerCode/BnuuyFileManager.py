import os
import json
from . import BnuyNumUI as ui
from . import BnuuyFolderManager as folder_manager
#### JSON INIT ####


"""Initializes bnuuyplayer jsons when called"""
# NewStart creates the necessary bnuuyplayer jsons when called as(comment below)
# try: raise NewStart
# except NewStart as e: e.create_hist()
class NewStart(Exception):
    def __init__(self, path,data):
        super().__init__(path)
        self.path = path
        self.hist_path = os.path.join(path, "BnuyPlayerHist.json")
        self.hist_backup1 = os.path.join(path, "BnuyBackup1.json")
        self.hist_backup2 = os.path.join(path, "BnuyBackup2.json")
        self.path_for_db = os.path.join(data.home_path(), "DO_NOT_DELETE.json")
        self.bulk_save = {}

    def create_hist(self):
        if not os.path.isfile(self.hist_path):
            with open(self.hist_path, "w") as f:
                json.dump(self.bulk_save, f, indent=2)

        if not os.path.isfile(self.hist_backup1):
            with open(self.hist_backup1, "w") as f:
                json.dump(self.bulk_save, f, indent=2)

        if not os.path.isfile(self.hist_backup2):
            with open(self.hist_backup2, "w") as f:
                json.dump(self.bulk_save, f, indent=2)

        if not os.path.isfile(self.path_for_db):
            with open(self.path_for_db, "w") as f:
                json.dump(self.path, f, indent=2)


class LoadAndRecov():
    def __init__(self, bnuydata):
        self.data = bnuydata
        self.hist_path = bnuydata.hist_path
        self.hist_backup1 = bnuydata.hist_backup1
        self.hist_backup2 = bnuydata.hist_backup2

    #### MOVE DATABASE ####
    def move_db(self, new_path):
        from shutil import move
        if self.data.bnuy_path == new_path:
            ui.general_exception("The database already exists in the selected path!")
            return

        if not os.path.isdir(new_path):
            ui.special_exception(f"{new_path} isnt a valid folder! Aborting..")
            return
        # this collects every file for movement
        stuff_in_old_db = []
        stuff_in_new_db = os.listdir(new_path)

        for file in os.listdir(self.data.bnuy_path):
            if file == "DO_NOT_DELETE.json": continue
            stuff_in_old_db.append(file)

        # this moves every file
        for file in stuff_in_old_db:
            try:
                src = os.path.join(self.data.bnuy_path, file)
                if file in stuff_in_new_db:
                    print(f"A file/folder already exists with the name of {file} already exists in the new path!")
                    print("Skipping..")
                    continue
                move(src, new_path)
                print(f"Moved) {file}")

            except PermissionError:
                ui.special_exception("Aborting!! BnuuyPlayer is missing permission from writing into that folder!")
                continue

            except OSError as e:
                print(f"{file} failed to move! Error below, continuing..")
                print(e)
                continue
        else:

            for num, tupl in self.data.song_paths.items():
                # ignore folders
                if folder_manager.bnuuyfolder_check(tupl): continue

                name, path, is_stream, funct = tupl
                # ignore streamed
                if is_stream: continue

                # This fixes the paths from the old bnuy_path into the new one!:3
                if self.data.bnuy_path in path:
                    # this cuts up the path
                    split_path = path.split(self.data.bnuy_path)
                    # rewrites the old path with the new one anr combines
                    split_path[0] = new_path
                    path = split_path[0] + split_path[1]
                    
                    # this ensures that the file/dir actually moved before rewriting
                    folder_not_exists = False
                    file_not_exists = False
                    if not os.path.isfile(path): file_not_exists = True
                    if not os.path.isdir(path): folder_not_exists = True
                    if file_not_exists and folder_not_exists: continue

                    # rewrites old entry
                    self.data.song_paths[num] = name, path, is_stream, funct

            tries = 0
            while tries < 2:
                try:
                    self.save_db_path()
                    print("Successfully saved changes!:3")
                    break
                except (OSError, PermissionError) as e:
                    if tries == 1:
                        print("Failed!:( Error is below, before quitting please note that your library is fine, but unlinked")
                        print(f"Fix the error and retry!\n\n{e}")
                        break
                    ui.special_exception("An unknown error occurred when saving the path, retrying 1 more time..")
                    tries += 1

            self.data.bnuy_path = new_path

            self.data.hist_path = os.path.join(new_path, "BnuyPlayerHist.json") 
            self.hist_path = os.path.join(new_path, "BnuyPlayerHist.json")

            self.data.hist_backup1 = os.path.join(new_path, "BnuyBackup1.json")
            self.hist_backup1 = os.path.join(new_path, "BnuyBackup1.json")

            self.data.hist_backup2 = os.path.join(new_path, "BnuyBackup2.json")
            self.hist_backup2 = os.path.join(new_path, "BnuyBackup2.json")

            self.data.keybind_dir = os.path.join(new_path, "bnuybinds.conf")

    #### SAVE DATABASE PATH ####

    def save_db_path(self):
        home_path = os.path.join(self.data.home_path(), "DO_NOT_DELETE.json")

        db_tmp_path = os.path.join(self.data.home_path(), "DO_NOT_DELETE.json.tmp")
        db_path = home_path

        with open(db_tmp_path, "w") as f:
            json.dump(self.data.bnuy_path, f)

        os.replace(db_tmp_path, db_path)

    #### SAVE DATABASE ####

    def saver(self):
        tmp_handler = {}

        tmp_path = os.path.join(self.data.bnuy_path, "BnuyPlayerHist.json.tmp")

        """Save compiler"""
        # Compiles every playlist into a temp dict to be saved.
        for num, tupl in self.data.song_paths.items():

            if folder_manager.bnuuyfolder_check(tupl):
                tmp_handler[num] = tupl

            else:
                (name, combined, is_stream, _) = tupl
                tmp_handler[num] = (name, combined, is_stream)

        # Assigns a local version of self.song_paths with audio_funct stripped
        save_song_paths = tmp_handler

        """Bulk save build"""
        # Compiles bulk save.
        self.data.bulk_save[0] = save_song_paths
        self.data.bulk_save[1] = self.data.initialized
        self.data.bulk_save[2] = self.data.no_hint
        self.data.bulk_save[3] = self.data.shuffl
        self.data.bulk_save[4] = self.data.time_used
        self.data.bulk_save[5] = self.data.time_playing
        self.data.bulk_save[6] = self.data.video
        self.data.bulk_save[7] = self.data.ram_allocated
        self.data.bulk_save[8] = self.data.gapless_toggle
        self.data.bulk_save[9] = list(self.data.valid_domains)

        successful_saves = 0
        """Atomic write to disk"""
        # Writes the tmp handler into the disk, first to hist_path, then backups
        # Ensures corruption cant occur via os.replace and backups
        # Uses successful saves to make sure all saves were uncorrupted

        try:
            with open(tmp_path, "w") as f:
                json.dump(self.data.bulk_save, f, indent=2)
            os.replace(tmp_path, self.hist_path)
            successful_saves += 1


            # Reads from main hist, write to backup1
            with open(self.hist_path, "r") as mainhist, open(self.hist_backup1, "w") as backup1:
                backup1.write(mainhist.read())
            successful_saves += 1

            # If it was successful, read backup1, write it to backup2
            if os.path.isfile(self.hist_backup1):
                with open(self.hist_backup1, "r") as backup1, open(self.hist_backup2, "w") as backup2:
                    backup2.write(backup1.read())
                successful_saves += 1

        except OSError as e:
            import sys
            print(f"Device ERROR during save, BnuuyPlayer is unable to work properly! Error message: \n\n{e}\n")
            print("Do not attempt to re-run BnuuyPlayer until this has been fixed! Your library could get corrupted.")
            print("Exiting for safety..")
            sys.exit()

        except FileNotFoundError:
            import sys
            print("BnuuyPlayer's database is missing! Emergency shutdown..")
            sys.exit()


    #### CORRUPTED HIST CREATOR ####

    def corr_backup(self):
        """Recovers backups for the user to manually recover"""

        success_reads = 1

        # Each successful read adds 1
        # if 1 failed it checks which failed, and rewrites with err msg

        while success_reads < 4:
            try:

                if success_reads == 1:
                    with open(self.hist_path) as f:
                        main = f.read()
                    success_reads += 1

                elif success_reads == 2:
                    with open(self.hist_backup1) as f:
                        backup1 = f.read()
                    success_reads += 1

                else:
                    with open(self.hist_backup2) as f:
                        backup2 = f.read()
                    success_reads += 1

            except(FileNotFoundError,OSError):

                if success_reads == 1: main = "UNREADABLE OR DELETED"

                elif success_reads == 2: backup1 = "UNREADABLE OR DELETED"

                else: backup2 = "UNREADABLE OR DELETED"

                success_reads += 1  



        ui.corr_last_stand(main, backup1, backup2)

        num = 0

        while True:

            """Backs up all available corrupted backups"""
            corr_path = os.path.join(self.data.bnuy_path, f"CorruptedBnuuyHist_{num}.json")
            corr_backup1 = os.path.join(self.data.bnuy_path, f"CorruptedBnuuyBackup_{num}.json")
            corr_backup2 = os.path.join(self.data.bnuy_path, f"CorruptedBnuuyBackup2_{num}.json")

            json_checker = os.path.isfile(corr_path)
            backup_checker = os.path.isfile(corr_backup1)
            backup_checker2 = os.path.isfile(corr_backup2)

            if json_checker or backup_checker or backup_checker2:
                num += 1
                continue

            # Checks if file exists, if it does it rewrites
            else:
                if os.path.isfile(self.hist_path):
                    os.rename(self.hist_path, corr_path)

                if os.path.isfile(self.hist_backup1):
                    os.rename(self.hist_backup1, corr_backup1)

                if os.path.isfile(self.hist_backup2):
                    os.rename(self.hist_backup2, corr_backup2)
                break




    #### HIST LOADER ####

    def loader_bunny(self, num):
        hists = {1: self.hist_path,
                 2: self.hist_backup1,
                 3: self.hist_backup2,}
        try:
            # attempts to load all hists, an error increments num
            # incrementing is done by processor
            path = hists[num]

            with open(path) as f:
                self.data.bulk_save = json.load(f)

        except(json.JSONDecodeError, AttributeError, SyntaxError, FileNotFoundError):
            # Returns back to processor to let it do the job of incrementing
            pass

    #### BUNNY RECOVERER ####

    def recovery_bunny(self, values):
        recov_attempts = 2

        recovered = {}
        failed = {}
        for key, method in values.items():


            while True:

                if self.data.bulk_save.get(key) is not None:

                    # Attempts to reassign the attribute to the newest file.
                    setattr(self.data, method, self.data.bulk_save.get(key))
                    recovered[key] = method
                    recov_attempts = 2
                    break

                elif recov_attempts == 4:

                    failed[key] = method
                    # Resets back to 1
                    recov_attempts = 2
                    break 

                else: 
                    self.loader_bunny(recov_attempts)
                    recov_attempts += 1 
                    continue

        return failed, recovered



    #### LOADSAVE FILE LOADER ####

    def processor(self):
        recov_attempts = 1

        self.loader_bunny(recov_attempts)

        # Dict keys match the JSON keys.
        lookup_registry = {
        "0": "song_paths",
        "1": "initialized",
        "2": "no_hint",
        "3": "shuffl",
        "4": "time_used",
        "5": "time_playing",
        "6": "video",
        "7": "ram_allocated",
        "8": "gapless_toggle",
        "9": "valid_domains",
        }
        domain_backup = {"youtube.com",
                        "youtu.be",
                        "music.youtube.com",
                        "soundcloud.com",
                        "bandcamp.com",
                        "dai.ly",
                        "vimeo.com",
                        "tiktok.com",
                        "vm.tiktok.com",
                        "dailymotion.com",
                        "old.reddit.com",
                        "v.redd.it",
                        "reddit.com",
                        "instagr.am",
                        "instagram.com",
                        "fb.watch",
                        "facebook.com",
                        "fb.com",
                        "audiomack.com",
                        "mixcloud.com"}


        failed_keys = {}

        for key, item in lookup_registry.items():
            # equivalent to e.g: self.song_paths = self.bulk_save.get("0")
            # setattr is required as self.item = ... would create an attribute 
            # named item rather than interacting with the actual items.
            setattr(self.data, item, self.data.bulk_save.get(key))

            # Checks for corrupted or failed keys, compiles to failed_keys
            if self.data.bulk_save.get(key) is None:
                failed_keys[key] = item

        """Song paths recoverer"""
        # this is used to make self.shuffl a list as a flag
        make_list = False


        if len(failed_keys) >= recov_attempts:

                failed, recovered = self.recovery_bunny(failed_keys)

                if "0" in failed:
                    """Song paths check"""
                    # this initiates a full panic(?) because the library is gone
                    self.corr_backup()
                    self.data.song_paths = {}
                    self.data.initialized = False
                    self.data.no_hint = False
                    self.data.video = False
                    self.data.shuffl = [False, "placeholder"]
                    self.data.gapless_toggle = False
                    self.data.time_used = 0
                    self.data.time_playing = 0
                    self.data.ram_allocated = 10 
                    self.data.valid_domains = domain_backup
                    failed.clear()
                    failed_keys.clear()
                    return

                make_list = False

                if "4" in failed: 
                    """Time used check"""
                    print("Your time used stat was corrupted/unrecoverable, setting to 0.")
                    del failed["4"]
                    self.data.time_used = 0

                if "5" in failed:
                    """Time playing check"""
                    print("Your time playing stat was corrupted/unrecoverable, setting to 0.")
                    self.data.time_playing = 0
                    del failed["5"]

                if "7" in failed:
                    """Allocated RAM"""
                    print("Allocated RAM config was lost, defaulting to 10mB")
                    self.data.ram_allocated = 10
                    del failed["7"]

                if "9" in failed:
                    print("Domain whitelist was lost!:( Defaulting to the original..")
                    self.data.valid_domains = domain_backup
                    del failed["9"]

                solved = []
                for key, method in failed.items():
                    while True:
                        if key == "1" or key == "2" or key == "3" or key == "6" or key == "8":
                            if key == "3": 
                                """Shuffl check"""
                                make_list = True

                            choices = {
                                "1": True, 
                                "2": False,
                                }

                            select = input(f"""A JSON entry was corrupted!
Entry) {method}

1) Set it to the True/on position.
2) Set it to the False/off position.

>>> """)
                            ui.term_cleaner()

                            selected_bool = choices.get(select)

                            if selected_bool is None:
                                ui.general_exception()
                                continue

                            if make_list:
                                selected_bool = [selected_bool, "placeholder"]
                                make_list = False

                            setattr(self.data, method, selected_bool)
                            solved.append(key)
                            break

                        else: break
                # Cleans up the failed keys
                for key in solved:
                    del failed[key]


        tmp_handler = {}
        err_paths = {}

        invalid_countr = 0
        
        """Playlist corr/valid sorter"""
        # Attempts to recover playlists, if it fails
        # it adds 1 to invalid countr, then adds it to err paths
        # if the playlist is recovered successfully, its put into tmp handler
        for num, tupl in self.data.song_paths.items():

            # This doesnt require integrity checks as it stores keys.
            if folder_manager.bnuuyfolder_check(tupl):
                tmp_handler[num] = tupl

            elif len(tupl) == 3:
                name, path, is_stream = tupl

                # Sorts working and non working paths, bad ones are DELETED
                if os.path.isdir(path) or is_stream is True:
                    tmp_handler[num] = (name, path, is_stream, self.data.BnuyDJ.audio_funct)
                else:
                    print(f"Found a invalid save at {path} \ndeleting to prevent bugs..")

            else:
                invalid_countr += 1
                print(f"""\nFound invalid save path, was the JSON edited/corrupted?
Found {invalid_countr} invalid save paths.
Corrupted/edited path) {tupl}""")

                err_paths[len(err_paths) + 1] = tupl

        if len(err_paths) > 0:
            print(f"Invalid saves list; {err_paths}")

        self.data.song_paths = tmp_handler # pushes recovered playlists back into the dict
        # Note: invalid songs are already scrubbed, theyre not included in tmp_handler

        tmp_db = {}
        # converts json string keys back into integers
        for key, tupl in self.data.song_paths.items():

            try:
                key = int(key)
            except ValueError:
                print(f"Invalid key was found, was the json modified?")
                print(f"Deleting the entry at key {key} for stability.")
                continue

            tmp_db[key] = tupl

        self.data.song_paths.clear()
        self.data.song_paths.update(tmp_db)


####### OTHER STUFF #######

## First time hist creation
def hist_creator(data):
    bnuy_file_stuff = LoadAndRecov(data)
    """Hist creator/checker/loader"""
    # Pulled from self, checks if the jsons actually exists.
    # If it doesnt exist, raise NewStart
    try:
        if not os.path.isfile(data.hist_path) and not os.path.isfile(data.hist_backup2) and not os.path.isfile(data.hist_backup1): 
            raise NewStart(data.bnuy_path, data)

        bnuy_file_stuff.processor()

    except NewStart as e:
        e.create_hist()

    
