import os
import time
from multiprocessing import Process

import requests

app_url = "127.0.0.1:8001"
http_url = f"http://{app_url}"
timeout = 10


def _runserver():
    os.system(f"wkz manage 'runserver {app_url} --noreload'")


def _get_site_status_code(url):
    return requests.get(url=url).status_code


def test_workoutizer_full():
    proc = Process(target=_runserver, args=())
    proc.start()

    # sleep for some seconds in order to have enough time to import activities
    time.sleep(timeout)

    # check that all pages are accessible
    assert _get_site_status_code(f"{http_url}") == 200
    assert _get_site_status_code(f"{http_url}/settings") == 200
    assert _get_site_status_code(f"{http_url}/help") == 200
    assert _get_site_status_code(f"{http_url}/sports") == 200
    assert _get_site_status_code(f"{http_url}/add-activity") == 200
    assert _get_site_status_code(f"{http_url}/add-sport") == 200
    for activity in range(1, 10):
        assert _get_site_status_code(f"{http_url}/activity/{activity}") == 200
    for sport in ['hiking', 'swimming', 'cycling', 'jogging', 'unknown']:
        assert _get_site_status_code(f"{http_url}/sport/{sport}") == 200

    print(f"SUCCESS - no errors found.")

    # end process
    proc.terminate()


if __name__ == '__main__':
    test_workoutizer_full()
