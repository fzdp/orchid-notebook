import wx
from pubsub import pub
from models import Note
from wx.lib.agw.pygauge import PyGauge
from config_manager import config


class StatusBar(wx.StatusBar):
    def __init__(self, parent):
        super().__init__(parent)

        self.SetFieldsCount(3)
        self.SetStatusWidths([-1, 70, 100])

        self.size_changed = False
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Bind(wx.EVT_IDLE, self.on_idle)

        self.SetStatusText("", 0)
        self.btn_todo_status = wx.Button(self, style=wx.NO_BORDER, size=(70, -1))
        self.btn_todo_status.SetLabelMarkup(self._get_todo_status_text(0,0))

        self.todo_progress = PyGauge(self, size=(100,-1), style=wx.GA_HORIZONTAL|wx.NO_BORDER)
        self.todo_progress.SetValue(0)
        self.todo_progress.SetBackgroundColour(wx.Colour(config.get('UI', 'todo_progress_bg_color')))
        self.todo_progress.SetBarGradient(
            (wx.Colour(config.get("UI","todo_progress_bg_start")), wx.Colour(config.get("UI", "todo_progress_bg_end")))
        )
        self.todo_progress.SetRange(1)

        self.do_position()
        self.Bind(wx.EVT_BUTTON, self.on_click_todo_status, self.btn_todo_status)
        pub.subscribe(self.on_note_show, 'on.note.show')
        pub.subscribe(self.on_todo_change, 'on.todo.change')
        pub.subscribe(self.on_note_hide, 'on.note.hide')

    def on_note_hide(self):
        self.btn_todo_status.SetLabelMarkup(self._get_todo_status_text(0,0))
        self.todo_progress.SetValue(0)
        self.todo_progress.Refresh()

    def on_todo_change(self, note_id):
        note = Note.find(note_id)
        self.on_note_show(note)

    def on_note_show(self, note):
        status = note.get_todo_status()
        self.btn_todo_status.SetLabelMarkup(self._get_todo_status_text(status['finished'],status['total']))
        progress = status['finished'] / status['total'] if status['total'] > 0 else 0
        self.todo_progress.SetValue(progress)
        self.todo_progress.Refresh()

    @staticmethod
    def on_click_todo_status(_):
        pub.sendMessage('on.todo_status.click')

    @staticmethod
    def _get_todo_status_text(finished, total):
        return '<span foreground="red" font_weight="bold" size="large">{}</span> ' \
               '<span size="large">/</span> '\
               '<span foreground="red" font_weight="bold" size="large">{}</span>'.format(finished,total)

    def on_size(self, evt):
        evt.Skip()
        self.do_position()
        self.size_changed = True

    def on_idle(self, evt):
        if self.size_changed:
            self.do_position()

    def do_position(self):
        rect = self.GetFieldRect(1)
        self.btn_todo_status.SetRect(rect)

        rect = self.GetFieldRect(2)
        self.todo_progress.SetRect(rect)

        self.sizeChanged = False