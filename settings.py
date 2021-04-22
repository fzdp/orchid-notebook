import wx
import os


SETTINGS = {}
SETTINGS['app_name'] = 'UltraNote'

# call this method in main.py when wx.App created
def setup():
    SETTINGS['app_dir'] = wx.StandardPaths.Get().GetUserLocalDataDir()
    SETTINGS['content_dir'] = os.path.join(SETTINGS['app_dir'], 'content')
    SETTINGS['db_dir'] = os.path.join(SETTINGS['app_dir'], 'local_db')
    SETTINGS['db_file'] = os.path.join(SETTINGS['db_dir'], 'note.sqlite')
    SETTINGS['index_dir'] = os.path.join(SETTINGS['app_dir'], 'index')
    SETTINGS['sqlite_config'] = dict(driver='sqlite',database=SETTINGS['db_file'])

SETTINGS['todo_finished_color'] = "#00FF00"
SETTINGS['todo_progress_bg_color'] = '#FFFFFF'
SETTINGS['todo_progress_bg_start'] = '#00FF00'
SETTINGS['todo_progress_bg_end'] = '#006600'
