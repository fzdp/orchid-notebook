import wx
import os
from config_manager import config
import sqlite3
from views import MainFrame
from utils import ApplicationUtil
import i18n

import builtins
builtins._ = i18n.t


def setup_translation():
    locales_dir = os.path.join(ApplicationUtil.bundle_dir(), 'assets', 'locales')
    i18n.load_path.append(locales_dir)
    i18n.set("filename_format", "{locale}.{format}")
    i18n.set("locale", config.get("APP", "language"))
    i18n.set("enable_memoization", True)


def setup_locale():
    config_language = config.get("APP", "language")
    if config_language == "en":
        wx.Locale(language=wx.LANGUAGE_ENGLISH_US)
    elif config_language == "cn":
        wx.Locale(language=wx.LANGUAGE_CHINESE_SIMPLIFIED)

    if wx.Platform == "__WXMSW__":
        import locale
        if config_language == "en":
            locale.setlocale(locale.LC_ALL, 'en-US.UTF-8')
        elif config_language == "cn":
            locale.setlocale(locale.LC_ALL, 'zh-CN.UTF-8')


def setup_db():
    db_file_existed = os.path.exists(config.get('PATH', 'db_file'))

    conn = sqlite3.connect(config.get("PATH", "db_file"))
    cursor = conn.cursor()

    if not db_file_existed:
        with open(os.path.join(ApplicationUtil.bundle_dir(),'assets','sqlite_schema.sql'),'r',encoding='utf-8') as f:
            schema_content = f.read()
        cursor.executescript(schema_content)
        conn.commit()

    notebook_count = cursor.execute("SELECT count(*) FROM notebooks").fetchone()[0]
    if not notebook_count:
        cursor.execute("insert into notebooks(name, description) values(?,?)", (
            _("notebook.initial_name"), _("notebook.initial_desc")))
        conn.commit()
    conn.close()


class App(wx.App):
    def OnInit(self):
        setup_locale()
        setup_translation()
        setup_db()
        return True


if __name__ == "__main__":
    app = App(False)
    frame = MainFrame()
    frame.Show()
    app.SetTopWindow(frame)
    app.MainLoop()
