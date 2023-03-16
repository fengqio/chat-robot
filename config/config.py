import configparser
import os

config_info = configparser.ConfigParser()


def read_sys_config_path():
    current_path = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(current_path, '../config.ini')
    config_info.read(config_file, encoding="utf-8")
    return config_info
