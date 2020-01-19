import os
from pathlib import Path
import datetime
import configparser

import dropbox


cwd = Path(os.path.abspath(__file__))
parent = cwd.parent.parent

config = configparser.ConfigParser()
config.read(os.path.join(parent, 'config.ini'))

dropbox_token = config.get('DROPBOX', 'dropbox_token')
dbx = dropbox.Dropbox(dropbox_token)

file = "db.sqlite3"


def upload_db():
    date = datetime.date.today()
    print(f"uploading {file} to dropbox ...")
    with open(f"{parent}/workoutizer/{file}", 'rb') as f:
        dbx.files_upload(f.read(), f"/workoutizer/backup/{date}_{file}")
    print("done.")


if __name__ == '__main__':
    upload_db()
