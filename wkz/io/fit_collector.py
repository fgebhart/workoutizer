import logging
import os
import shutil
from typing import List, Union

log = logging.getLogger(__name__)


ACTIVITY_DIR_NAME = "Activity"
NESTED_DIR_DEPTH = 4


def collect_fit_files_from_device(
    path_to_garmin_device: str,
    target_location: str,
    delete_files_after_import: bool = False,
) -> int:
    sub_dir_for_garmin_files = "garmin"
    target_location = os.path.join(target_location, sub_dir_for_garmin_files)
    if not os.path.isdir(target_location):
        os.makedirs(target_location)
    return copy_fit_files(path_to_garmin_device, target_location, delete_files_after_import)


def copy_fit_files(path_to_garmin_device: str, target_location: str, delete_files_after_import: bool) -> int:
    log.debug(f"looking for new activity files in garmin device at {path_to_garmin_device}")
    activity_path = _find_activity_sub_dir_in_path(
        name_of_dir=ACTIVITY_DIR_NAME,
        path=path_to_garmin_device,
        depth=NESTED_DIR_DEPTH,
    )
    n_files_copied = 0
    if activity_path:
        log.debug(f"found activity dir at: {activity_path}")
        fits = [
            os.path.join(root, name)
            for root, dirs, files in os.walk(activity_path)
            for name in files
            # Some devices genereate file named .FIT, other .fit
            if name.lower().endswith(".fit")
        ]
        if fits:
            for fit in fits:
                file_name = os.path.basename(fit)
                target_file = os.path.join(target_location, file_name)
                if not os.path.isfile(target_file):
                    shutil.copy(fit, target_file)
                    log.info(f"copied file: {target_file}")
                    n_files_copied += 1
                    if delete_files_after_import:
                        os.remove(fit)
                        log.debug(f"deleted fit file from device: {file_name}")
            if n_files_copied == 0:
                log.info("No new file found.")
        else:
            log.debug(f"Could not find any activity fit files at {activity_path}")
    else:
        log.warning(f"No directory named '{ACTIVITY_DIR_NAME}' found in path {path_to_garmin_device}")
    return n_files_copied


def _find_activity_sub_dir_in_path(name_of_dir: str, path: str, depth: int = 3) -> Union[str, bool]:
    def _get_all_subfolders(paths: List[str]) -> List[str]:
        sub_dirs = []
        for path in paths:
            sub_dirs += [f for f in os.scandir(path) if f.is_dir()]
        return sub_dirs

    paths = [path]
    for _ in range(depth):
        sub_dirs = _get_all_subfolders(paths)
        for sub_dir in sub_dirs:
            if name_of_dir.lower() == sub_dir.name.lower():
                return sub_dir.path
        paths = sub_dirs
    # if this line is reach it means the dir was not found
    return False
