import os
import subprocess
from threading import Thread
from . import BnuyNumUI as ui
from . import BnuuyFolderManager as folder_manager
from shutil import which
# escape from loops
class Escape(Exception): pass

class BnuuyDJ():
    def __init__(self, bnuydata):
        self.data = bnuydata

    #### PLAYLIST PICKER ####

    def playlist_picker(self):
        while True:

            try:

                countr = 0

                res = self.data.lib_print(local_only=False)
                display_keys = res.get("display_keys")

                choice = ui.playlist_main_menu()

                countr = 0
                tmp_song = {}

                # causes audio funct to raise ValueError, causing a return to main menu
                if choice == "0": return choice, countr

                elif choice.lower() == "s":
                    self.data.investibun_search()
                    continue

                elif choice.lower() == "as":
                    self.data.advanced_investibunny()
                    continue

                elif choice.lower() == "dl":
                    self.data.lrc_dl()
                    continue

                else: choice = int(choice)

                # defines values that local song picker requires
                choice = display_keys[choice][0]
                
                tupl = self.data.song_paths[choice]
                liked_handler = False

                if folder_manager.bnuuyfolder_check(tupl):
                    res = self.data.BnuyFolder.bnuuyfolder_manager(tupl)

                    if res is not None:
                        values = res.get("selected")

                        if values is None: 
                            liked_handler = True
                            path = res
                            is_stream = True
                        # return route
                    else: continue

                    # regular route
                    if values is not None:
                        name, path, is_stream, function = values

                else: name, path, is_stream, function = tupl
                if not liked_handler:
                    if not os.path.isdir(path) and is_stream is False:
                        ui.term_cleaner()
                        print("The original folder is missing, did you move it or delete it?")
                        print("Deleting playlist for stability..")
                        self.data.internal_delete(choice)
                        continue

                picker_skip = False
                # prints every local song in current song path playlist
                # splits the extension from songname, compares to invalid ext
                # if it is in invalid ext it skips, otherwise print
                if liked_handler is False and is_stream is False:
                    invalid_ext = {".midi", ".mid", ".mod", ".xm", ".s3m", ".wma", ".lrc"}

                    for song in os.listdir(path):
                        filename, ext = os.path.splitext(song)

                        if ext not in invalid_ext:
                            filepath = os.path.join(path, song)
                            countr += 1
                            print(f"{countr}) {filename}")
                            tmp_song[countr] = filepath

                # liked handler printer
                elif liked_handler is True:
                    disp_keys = {}
                    for num, song in res.items():
                        disp_keys[len(disp_keys)+1] = num, song

                    for key, (og_key, song) in disp_keys.items():
                        print(f"{key}) {os.path.basename(os.path.splitext(song)[0])}")
                        tmp_song[og_key] = song

                else:
                    # This prevents the second error message below from going off
                    tmp_song[len(tmp_song)+1] = ""
                    print(
                    "Warning: Individual song picking is unsupported for streaming due to technical limitations."
                    )
                    picker_skip = True

                # Checks if the song path dict is empty, otherwise act normal
                selection_loop = True
                restart = False
                while selection_loop:

                    if len(tmp_song) < 1:
                        print("Playlist is empty.")

                    if not picker_skip:
                        choice = ui.song_picker_menu()
                        if choice == "0":
                            restart = True
                            break

                    else: 
                        choice = "1"
                        break

                    tmp_choice = choice.split()

                    if len(tmp_choice) == 2:
                        num = int(tmp_choice[0])
                        cmd = tmp_choice[1].lower()
                        path = tmp_song[num]
                        params = {
                            "num": num,
                            "cmd": cmd,
                            "path": path,
                            "songs": tmp_song,
                            }

                        res = self.data.cmd_handler(params)
                        # res is only not none when a indiv song is to be played
                        if res is None:
                            for num, file in tmp_song.items():
                                print(f"{num}) {os.path.basename(os.path.splitext(file)[0])}")
                            continue

                        else:
                            liked_handler = False
                            break

                    else: 
                        choice = int(choice)
                        break

                if restart: continue

                elif choice == 1: pass 
                elif liked_handler is False and choice < 2: pass
                # automatically moves on, no need for extra logic

                else: raise ValueError 

                if not liked_handler: path = [path]
                else: path = [*path.values()]

                player = [
                    "mpv",
                    *path,
                    f"--input-conf={self.data.keybind_dir}",
                    "--profile=fast",
                    "--no-video",
                    "--cache",
                    f"--demuxer-max-bytes={self.data.ram_allocated}m",
                    ]

                if len(path) < 1:
                    print("The file sys folder is empty! Try putting a song in it.")
                    print("Aborting playback attempt..")
                    continue


                if self.data.video: player.remove("--no-video")

                # f"--input-ipc-server={self.bnuy_path}/.mpv_socket"
                # saving this here for when i have a laptop/pc.

                if self.data.shuffl[0]: player.append("--shuffle")

                if self.data.gapless_toggle: player.append("--gapless-audio=yes")

                ui.term_cleaner()

                return player

            except (KeyError, ValueError):
                ui.general_exception()
                continue


            except Escape:
                continue

    def audio_funct(self):
        while True:
            player = self.playlist_picker()
            # return from song menu picker
            if player is None: 
                ui.term_cleaner()
                continue
            # return from main picker menu
            elif player == ("0", 0): return
            else: break

        if which("mpv") is None:
            print("Install MPV to access audio playback!")
            print("You can install MPV by reading bnuuyplayer's github README.md and folloeing the guide.")
            return

        print("")

        playing_countr = Thread(target=self.data.time_playing_counter, daemon=True)
        playing_countr.start()

        try:
            # lrc_thrd = threading.Thread(target=lrc_funct, daemon=True)
            # lrc_thrd.start()
            ui.binding_menu()
            subprocess.run(player, check=True)

        except(subprocess.CalledProcessError) as e:
            print(f"Error occurred during playback! Error msg: {e}")
        self.data.stop_playing_counter = True
        self.data.BnuyFileManager.saver()
        self.data.stop_playing_counter = False
