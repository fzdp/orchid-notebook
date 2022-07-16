import os
from configparser import ConfigParser
from appdirs import user_data_dir


class ConfigManager:
    def __init__(self):
        self.config_file = None
        self.config_dict = None

    # get("UI.language") or get("UI", "language")
    def get(self, *keys):
        if len(keys) == 1:
            keys = keys[0].split(".")
        return self.config_dict.get(*keys)

    def getboolean(self, *keys):
        if len(keys) == 1:
            keys = keys[0].split(".")
        return self.config_dict.getboolean(*keys)

    # set("UI.language", "en") or set("UI", "language", "en")
    def set(self, *keys_and_value):
        if len(keys_and_value) == 2:
            keys_and_value = keys_and_value[0].split(".") + [keys_and_value[1]]
        self.config_dict.set(*keys_and_value)
        self._save_config()

    def init(self):
        data_dir = self._get_app_data_dir()
        if not os.path.exists(data_dir):
            os.mkdir(data_dir)

        self.config_file = os.path.join(data_dir, "config.ini")

        if os.path.exists(self.config_file):
            self.config_dict = ConfigParser()
            self.config_dict.read(self.config_file)
        else:
            self.config_dict = self._get_default_config()
            self._save_config()

        self._ensure_dir_exists()
        return self

    def _save_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config_dict.write(configfile)

    def _ensure_dir_exists(self):
        dir_list = [self.get("PATH", "data_dir"), self.get("PATH", "notes_dir"), self.get("PATH", "notes_index_dir")]
        for dir_item in dir_list:
            if not os.path.exists(dir_item):
                os.mkdir(dir_item)

    @classmethod
    def _get_app_data_dir(cls):
        return user_data_dir(appname="OrchidNote", appauthor=False)

    @classmethod
    def _get_default_config(cls):
        app_data_dir = cls._get_app_data_dir()
        note_data_dir = os.path.join(app_data_dir, "default_notes")
        config_parser = ConfigParser()
        config_parser["DEFAULT"] = {
            "data_dir": note_data_dir,
            "db_file": os.path.join(note_data_dir, "note.sqlite"),
            "notes_dir": os.path.join(note_data_dir, "notes"),
            "notes_index_dir": os.path.join(note_data_dir, "notes_index"),
            "language": "en"
        }
        config_parser["PATH"] = {
            "db_file": os.path.join(app_data_dir, "note.sqlite"),
            "notes_dir": os.path.join(app_data_dir, "notes"),
            "notes_index_dir": os.path.join(app_data_dir, "notes_index")
        }
        config_parser["APP"] = {
            "language": "en",
            "window_title": "Orchid Note"
        }
        config_parser["UI"] = {
            "todo_finished_color": "#00FF00",
            "todo_progress_bg_color": "#FFFFFF",
            "todo_progress_bg_start": "#00FF00",
            "todo_progress_bg_end": '#006600'
        }
        return config_parser


config = ConfigManager().init()
