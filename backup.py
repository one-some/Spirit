import os
import shutil
import threading
import time
from config import config, data_path

def backup_data() -> None:
    """Backs up data to a specified backup folder."""

    location = config["backup"]["location"]

    for data_file in ["spirit.db", "prizes.json"]:
        shutil.copy(data_path(data_file), location)
    print(f"[backup] Automatically backed up data to {location}")

def backup_worker() -> None:
    while True:
        backup_data()
        time.sleep(int(config["backup"]["interval"]))

def start_backup_loop() -> None:
    t = threading.Thread(target=backup_worker)
    t.start()