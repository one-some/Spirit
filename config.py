import os
import configparser

config = configparser.ConfigParser()
config.read("config.ini")

def data_path(path: str) -> str:
    return os.path.join(config["data"]["location"], path)