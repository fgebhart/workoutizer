import os
from pathlib import Path
import datetime

import dropbox


dbx = dropbox.Dropbox(os.environ['DROPBOXTOKEN'])

file = "db.sqlite3"

if __name__ == '__main__':
    cwd = Path(os.path.abspath(__file__))
    parent = cwd.parent.parent

    date = datetime.date.today()

    print(f"uploading {file} to dropbox ...")
    with open(f"{parent}/workoutizer/{file}", 'rb') as f:
        dbx.files_upload(f.read(), f"/workoutizer/backup/{date}_{file}")
    print("done.")
