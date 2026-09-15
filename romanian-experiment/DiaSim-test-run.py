import os
import sys

class add_path():
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass

# TODO you need to fix this line below based on where DiaSim and romanian-cfr are locally, potentially
PATH_TO_DIASIM = os.path.join("..","..","..","DiaSim")
PATH_TO_ROMANIAN_CFR = os.path.join("..","..","..","romanian-cfr")

#BaseCLER is used locally though.

with add_path(PATH_TO_DIASIM):
    import UTILS

UTILS.compareCascades(os.path.join(PATH_TO_ROMANIAN_CFR),"RoLLex.txt",
    "BaseCLER",
    sys.argv[1],
    "comparison-BaseCLER-"+sys.argv[2])


