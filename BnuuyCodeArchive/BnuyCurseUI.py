import sys
import curses

class BnuyCursedUI():

    def __init__(self):
        # initializes curses
        self.stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.start_color()
        curses.use_default_colors()
        # white text on red bg, reserved for error text
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_RED)
        # red text, reserved for error borders
        curses.init_pair(2, curses.COLOR_RED, -1)
        self.stdscr.keypad(True)
        self.max_y, self.max_x = self.stdscr.getmaxyx()
        sys.excepthook = self.bnuycurse_except_hook


        # RULES:
        # 1: Coordinates 0,0 are reserved for input validation and warnings
        # 2: 1 is reserved for menus

        # 3: Inputs should always be located at 15,0 
        # 3.1: If an error/message goes paat 15,0 then it must be cleared/truncatable

    def refresh(self): self.stdscr.refresh()

    def bnuycurse_except_hook(self, exctype, value, traceback):
        curses.endwin()
        sys.__excepthook__(exctype, value, traceback)

    def max_y_check(self):
        # height
        if self.max_y < 15:
            self.stdscr.addstr(0,0,f"Please increase your terminal scale! Currently) {self.max_y}, expected greater than 15")
            from sys import exit as ex
            curses.endwin()
            ex()
        elif self.max_y < 30:
            self.special_exception(f"Warning: BnuuyPlayer recommends a terminal scale of 60/60, yours is {self.max_y}/{self.max_x}")

    def max_x_check(self):
        if self.max_x < 60: return self.max_x
        else: return 60

    ##### GENERAL METHODS #####

    def term_cleaner(self):
        self.stdscr.clear()
        self.refresh()

    def general_exception(self, xtra_text=""):
        self.term_cleaner()
        err_text = "Invalid input!:("
        self.stdscr.addstr(0, 0, err_text, curses.color_pair(1))
        if xtra_text != "":
            self.stdscr.addstr(0, len(err_text)+1, xtra_text, curses.color_pair(1))

        self.refresh()

    def special_exception(self, err_text):
        self.term_cleaner()
        self.stdscr.addstr(0,0, err_text, curses.color_pair(1))
        self.refresh()


    def bad_folder_names(self):
        self.term_cleaner()
        colums = self.max_x_check()

        """Err info boxes"""
        if self.max_y >= 4:
            invalid_names_box = self.stdscr.subwin(3,colums, 1,0)
            invalid_names_box.attrset(curses.color_pair(2))
            invalid_names_box.box()
        else: self.stdscr.addstr(0,0, "Invalid folder name entered, Note from dev: EXPAND your terminal, BnuuyPlayer is unlikely to function properly!")

        if self.max_y >= 8:
            intern_box_1 = self.stdscr.subwin(4,colums, 4,0)
            intern_box_1.box()

        """OS Boxes"""
        if self.max_y >= 19: 
            windows_box = self.stdscr.subwin(10,colums, 8,0)
            windows_box.box()

        if self.max_y >= 27:
            linux_box = self.stdscr.subwin(7,colums, 18,0)
            linux_box.box()

        if self.max_y >= 32:
            android_box = self.stdscr.subwin(6,colums, 25,0)
            android_box.box()

        if self.max_y >= 39:
            macos_box = self.stdscr.subwin(5,colums, 31,0)
            macos_box.box()

        """Other boxes"""
        if self.max_y >= 48:
            bnuuyplayer_box = self.stdscr.subwin(8,colums, 36,0)
            bnuuyplayer_box.box()

        """Populating the boxes"""
        # Invalid names box
        if self.max_y >= 4:
            self.stdscr.addstr(2,1,"Unknown Error. You likely used an invalid character/name.", curses.color_pair(1))
        else:
            self.stdscr.addstr(0,0,"Unknown Error. You likely used an invalid character/name. Note: If you see this, your terminal scale is too small. Please increase it so BnuuyPlayer can work properly.")

        # intern box
        if self.max_y >= 8:
            self.stdscr.addstr(5,1,"Invalid character/name list.")
            self.stdscr.addstr(6,1,"Note: If you dont see the list, increase terminal scale.")



        #### windows ####
        if self.max_y >= 19:
            self.stdscr.addstr(9,1,"Windows:")
            self.stdscr.addstr(10,1,'< > : - " / \\ | ? *')

            self.stdscr.addstr(12,1,"CON, PRN, AUX")
            self.stdscr.addstr(13,1,"NUL COM1, COM2, COM3, COM4, COM5, COM6, COM7, COM8, COM9")
            self.stdscr.addstr(14,1,"LPT1, LPT2, LPT3, LPT4, LPT5, LPT6, LPT7, LPT8, LPT9")

            self.stdscr.addstr(15,1,"0-31 (ASCII control characters)")
            self.stdscr.addstr(16,1,"Names also cannot end in a dot or space.")

        #### Linux ####
        if self.max_y >= 27:
            self.stdscr.addstr(19,1,"Linux:")
            self.stdscr.addstr(20,1,"0 (NULL byte)")
            self.stdscr.addstr(21,1,"/")
            self.stdscr.addstr(22,1,". (special name referring to current directory)")
            self.stdscr.addstr(23,1,".. (special name referring to parent directory)")

        #### Android ####
        if self.max_y >= 32:
            self.stdscr.addstr(26,1,"Android:")
            self.stdscr.addstr(27,1,'< > : - " / \\ | ? *')
            self.stdscr.addstr(28,1,"\\n")
            self.stdscr.addstr(29,1,"0-31 (ASCII control characters)")

        #### MacOS ####
        if self.max_y >= 39:
            self.stdscr.addstr(32,1,"MacOS")
            self.stdscr.addstr(33,1,":")
            self.stdscr.addstr(34,1,"/")

        #### Other ####
        if self.max_y >= 48:
            self.stdscr.addstr(37,1,"BnuuyPlayer:")
            self.stdscr.addstr(38,1,"BnuyPlayerHist.json")
            self.stdscr.addstr(39,1,"BnuyBackup1.json")
            self.stdscr.addstr(40,1,"BnuyBackup2.json")
            self.stdscr.addstr(41,1,"DO_NOT_DELETE.json")
            self.stdscr.addstr(42,1,"bnuybinds.conf")

        self.refresh()

    #### GENERAL INPUTS ####
    def input_helper(self):
        # This code provides a similar experience to python's input()
        # i think atleast, i cant test this till everything is complete QwQ
        text = [""]
        while True:

            self.stdscr.addstr(15,0,text[0])
            self.refresh()
            try:
                usr_input = self.stdscr.getch(15,len(text[0]))
            except curses.error: continue

            if usr_input in (curses.KEY_ENTER, 10,13):
                return text[0]

            elif usr_input in (curses.KEY_BACKSPACE, 127, 8):
                text[0] = text[0][:-1]
                self.stdscr.move(15,len(text[0]))
                self.stdscr.clrtoeol()
                self.refresh()
                continue

            elif usr_input in (curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT):
                if len(text[0]) == 0: continue
                else: continue
                #else: return usr_input
                # temp unwired

            elif usr_input in range(0,32): continue
            elif usr_input in (curses.KEY_HOME, curses.KEY_END, curses.KEY_PPAGE, curses.KEY_NPAGE, curses.KEY_RESIZE): continue

            usr_input = chr(usr_input)
            text[0] += usr_input
            if len(text[0]) >= self.max_x:
                self.stdscr.addstr(0,0, "ERROR: Exceeded character limit, increase terminal size for a larger limit!")
                text[0] = text[0][:-1]

    def intput(self):
        # callers are expected to do try/excepts
        text = self.input_helper()
        return int(text)

    def strput(self):
        # no conversion needed, input helper provides str by default
        # arrow keys will be managed soon, this is currently intended
        return self.input_helper()

    def binding_menu(self):
        self.term_cleaner()
        y_pos = 2
        columns = self.max_x_check()
        if self.max_y < 18: max_lines = self.max_y
        else: max_lines = 18

        keybind_box = self.stdscr.subwin(max_lines-1,columns, 1,0)
        keybind_box.box()

        keybindings = [
                "Default keybindings menu",
                "q) Stop playback",
                "Q) Stop playback and save progress",
                "l) Loop current song",
                "m) Mute",
                "i) Show extra information",
                "Backspace) Reset playback speed to normal",
                "P) Show progress",
                "p / space) Pause",
                "< / >) Go back/forward in the playlist.",
                "[ / ]) -10% / +10% playback speed",
                "{ / }) Half / double playback speed",
                "9 / 0) -2% / +2% volume",
                "b / s) back 30s / skip 30s",
                "F / G) Decrease / Increase subtitle size (Video only)",
                ] 

        for keybind in keybindings:
            if y_pos >= self.max_y-1: break
            elif len(keybind) > self.max_y: continue
            self.stdscr.addstr(y_pos, 1, keybind)
            y_pos += 1

        self.refresh()

    def adder_menu(self):
        self.term_cleaner()
        columns = self.max_x_check()

        if self.max_y >= 6:
            abs_path_box = self.stdscr.subwin(5,columns, 1,0)
            abs_path_box.box()

        if self.max_y >= 10:
            make_folder_box = self.stdscr.subwin(3,columns, 7,0)
            make_folder_box.box()

        if self.max_y >= 14:
            search_folder_box = self.stdscr.subwin(4,columns, 10,0)
            search_folder_box.box()

        if self.max_y >= 33:
            download_box = self.stdscr.subwin(18,columns, 15,0)

            if columns < 50: tmp_columns = self.max_x-1
            else: tmp_columns = 50

            download_box_internal = self.stdscr.subwin(8,tmp_columns, 21,1)
            download_box.box()
            download_box_internal.box()

        if self.max_y >= 37:
            back_box = self.stdscr.subwin(4,columns, 33,0)
            back_box.box()

        """Populating boxes"""

        # abs path 
        if self.max_y >= 6:
            self.stdscr.addstr(2,1,"▼ Playlist methods. ▼")

            self.stdscr.addstr(4,1,"1) Specify the path to your own folder.")

        # make folder
        if self.max_y >= 10:
            self.stdscr.addstr(8,1,"2) Allow BnuuyPlayer to make a folder automatically.")

        # search for folder
        if self.max_y >= 13:
            self.stdscr.addstr(11,1,"3) Allow BnuuyPlayer to search for a specified folder.")
            self.stdscr.addstr(12,2,"(BnuuyPlayer can only search within the folder it's in.)")

        # download box
        if self.max_y >= 30:
            self.stdscr.addstr(16,1,"4) Online download/stream.")
            self.stdscr.addstr(17,2,"(Downloading will take up a chunk of storage.)")
            self.stdscr.addstr(18,2,"(Supported sites below.)")

        # download internal box
        if self.max_y >= 37:
            self.stdscr.addstr(21,2,"▼ Social media ▼")
            self.stdscr.addstr(22,4,"YouTube, TikTok, Reddit, FaceBook, Instagram")

            self.stdscr.addstr(24,2,"▼ Music and Audio ▼")
            self.stdscr.addstr(25,4,"bandcamp, audiomack, mixcloud, soundcloud")

            self.stdscr.addstr(26,2,"▼ Other ▼")
            self.stdscr.addstr(27,4,"vimeo, dailymotion")

        # back
        if self.max_y >= 37:
            self.stdscr.addstr(35,1, "0) Skip/back.")
        else: self.stdscr.addstr(0,0, f"0) Skip/Back, Warning: Recommended terminal scale: 60/50+, yours is) {self.max_y}/{self.max_x}")

        self.refresh()
