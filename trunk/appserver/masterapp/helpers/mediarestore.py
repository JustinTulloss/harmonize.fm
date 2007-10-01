import os

DB = "music.db"
UPLOAD_DIR = "tmp"
STORAGE_DIR = "media"

here = os.getcwd()
try:
    os.remove(here + os.sep+DB)
except:
    pass

def cleandir(path):
    for file in os.listdir(path):
        if os.path.isfile(file):
            os.remove(file)

cleandir(here + os.sep + UPLOAD_DIR)
cleandir(here + os.sep + STORAGE_DIR)

args = ["paster", "setup-app", "development.ini"]
os.spawnvp(os.P_WAIT,"paster", args)
