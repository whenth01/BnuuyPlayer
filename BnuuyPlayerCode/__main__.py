import sys
try:
    from . import BnuuyPlayerCore
except ModuleNotFoundError:
    print("BnuuyPlayer's core file is missing, please reinstall BnuuyPlayer!")
    sys.exit()

BnuuyPlayerCore.start()
