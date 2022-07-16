import wx
from pubsub import pub
from .popup_menu_mixin import PopupMenuMixin


class NotePreviewPanel(wx.Panel, PopupMenuMixin):
    DEFAULT_BACKGROUND_COLOR = wx.Colour(255,255,255)
    HIGHLIGHT_BACKGROUND_COLOR = wx.Colour(219, 219, 219)

    def __init__(self, parent, note):
        super().__init__(parent, size=(-1, 110), style=wx.BORDER_NONE, name=self.get_name_by_note_id(note.id))
        self.note_id = note.id
        self.parent = parent
        self.builder_ui(note)

        self.Bind(wx.EVT_LEFT_UP, self.on_left_up)

        menu_params = [
            dict(item=_("note.duplicate"), handler=self.copy_note),
            dict(item=_("note.move"), handler=self.move_note),
            dict(kind=wx.ITEM_SEPARATOR),
            dict(item=_("note.delete"), handler=self.delete_note)
        ]
        self.setup_popup_menu(menu_params, self, wx.EVT_CONTEXT_MENU)

    @staticmethod
    def get_name_by_note_id(note_id):
        return 'note_{}'.format(note_id)

    def delete_note(self, evt):
        pub.sendMessage('on.note.delete', note_id=self.note_id)

    def move_note(self, e):
        pub.sendMessage('on.note.move', note_id=self.note_id)

    def copy_note(self, evt):
        pub.sendMessage('on.note.copy', note_id=self.note_id)

    def on_left_up(self, evt):
        evt.Skip()
        pub.sendMessage('note.show', note_id=self.note_id)

    def builder_ui(self, note):
        v_sizer = wx.BoxSizer(wx.VERTICAL)
        self.st_note_title = wx.StaticText(self,style=wx.ST_ELLIPSIZE_END)
        self.st_note_preview = wx.StaticText(self,style=wx.ST_ELLIPSIZE_END)
        self.st_note_date = wx.StaticText(self)

        self.st_note_title.SetFont(wx.Font(wx.FontInfo(14).Bold()))
        self.st_note_preview.SetFont(wx.Font(wx.FontInfo(14).Light()))
        self.st_note_preview.SetOwnForegroundColour(wx.Colour(78,78,78))
        self.st_note_date.SetOwnForegroundColour("#D61C4E")

        self.refresh(note)

        v_sizer.Add(self.st_note_title, flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        v_sizer.AddSpacer(15)
        v_sizer.Add(self.st_note_preview, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        v_sizer.AddStretchSpacer(1)
        v_sizer.Add(self.st_note_date, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        line = wx.StaticLine(self, size=(-1, 1))
        line.SetBackgroundColour("#cbcbcb")
        v_sizer.Add(line, flag=wx.EXPAND)

        self.SetSizer(v_sizer)
        self.undo_highlight()

    def refresh(self, note):
        self.note_id = note.id
        self.update_title(note.title)
        self.update_content(note.snippet)
        self.update_time(note.updated_at)

    def update_content(self, content):
        if self.st_note_preview.GetLabel()[:100] != content[:100]:
            self.st_note_preview.SetLabel(content)

    def update_title(self, title):
        if not title:
            title = _("note.default_title")
        self.st_note_title.SetLabel(title)

    def update_time(self, updated_at):
        self.st_note_date.SetLabel(updated_at.strftime('%Y-%m-%d %H:%M'))

    def undo_highlight(self):
        self.SetBackgroundColour(self.DEFAULT_BACKGROUND_COLOR)
        self.Refresh()

    def highlight(self):
        self.SetBackgroundColour(self.HIGHLIGHT_BACKGROUND_COLOR)
        self.Refresh()
