#!/usr/bin/python3 -u
import time
import os
import shutil


path_to_gvfs = "/run/user/1000/gvfs/"
target_location = "/home/fabian/Documents/Dropbox/my_tracks/garmin/"
activity = "/Primary/GARMIN/Activity/"


if __name__ == '__main__':
    print(f"looking for garmin device in: {path_to_gvfs}")
    while True:
        garmin_watch = [os.path.join(root, name) for root, dirs, files in os.walk(path_to_gvfs)
                        for name in dirs if name.startswith("mtp:host")]
        if garmin_watch:
            garmin_watch = garmin_watch[0] + activity
            if os.path.isdir(garmin_watch):
                fits = [os.path.join(root, name) for root, dirs, files in os.walk(garmin_watch)
                        for name in files if name.endswith(".fit")]
                for fit in fits:
                    file_name = str(fit.split("/")[-1])
                    target_file = target_location + file_name
                    if not os.path.isfile(target_file):
                        shutil.copy(fit, target_file)
                        print(f"copied file: {file_name}")
        time.sleep(5)
