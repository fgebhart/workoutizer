import os
from pathlib import Path
import dropbox


dbx = dropbox.Dropbox(os.environ['DROPBOXTOKEN'])

file = "workoutizer/db.sqlite3"

if __name__ == '__main__':
    cwd = Path(os.path.abspath(__file__))
    parent = cwd.parent.parent

    print(f"downloading {file} from dropbox ...")
    with open(f"{parent}/{file}", "wb") as f:
        metadata, res = dbx.files_download(path=f"/{file}")
        f.write(res.content)
    print("done.")
