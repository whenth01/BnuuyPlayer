import sys
from . import BnuuyFileManager
from . import BnuuyPlayerCore
file_manager = BnuuyFileManager

__version__ = "1.0.8"

#### EXCEPT HOOK ####
def bnuy_except_hook(exctype, value, traceback):
    """Custom messages for exceptions"""

    # Specific error handling to make specific cases not crash the code.
    if exctype == KeyboardInterrupt: 
        print("\n\nTurning off.. Thank you for using BnuuyPlayer!")
        try:
            data = BnuuyPlayerCore.bnuuyplayer_state(BnuuyPlayerCore.db_ref, "return pls:3")
            full_data = data["bnuuydb"]
            file_manager.LoadAndRecov.saver(full_data)

        except KeyError: 
            # no need to save if the initialization wasnt far enough
            pass
        sys.exit()

    elif exctype == IsADirectoryError:
        print("""IsADirectoryError occurred!
A folder you created is conflicting with BnuuyPlayer's files, please rename or delete it!

Please rename the folder or delete it to use BnuuyPlayer.""")
        sys.exit()
    else:
        sys.__excepthook__(exctype, value, traceback)
sys.excepthook = bnuy_except_hook
