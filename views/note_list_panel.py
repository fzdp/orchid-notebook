import wx
from .note_preview_panel import NotePreviewPanel
import wx.lib.scrolledpanel as scrolled
import images


class NoteListPanel(scrolled.ScrolledPanel):
    def __init__(self, parent):
        super().__init__(parent)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.empty_msg_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.empty_msg_sizer, flag=wx.EXPAND, proportion=1)

        self.empty_msg_sizer.AddStretchSpacer()
        self.empty_msg_sizer.Add(wx.StaticBitmap(self, bitmap=images.empty_note.GetBitmap()),flag=wx.CENTER)
        self.empty_msg_sizer.Add(wx.StaticText(self, label=_("note_list_panel.empty_note")),flag=wx.CENTER|wx.TOP,border=10)
        self.empty_msg_sizer.AddStretchSpacer()

        self.list_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.list_sizer, flag=wx.EXPAND, proportion=1)
        self.SetSizer(self.main_sizer)

        self.SetBackgroundColour(wx.WHITE)

    def show_empty_msg(self, show=True):
        if show and not self.main_sizer.IsShown(self.empty_msg_sizer):
            self.main_sizer.Show(self.empty_msg_sizer, True)
        if not show and self.main_sizer.IsShown(self.empty_msg_sizer):
            self.main_sizer.Show(self.empty_msg_sizer, False)

    def add(self, notes):
        if not notes:
            self.show_empty_msg()
            self.SetupScrolling(scroll_x=False)
            return False
        self.show_empty_msg(False)

        if isinstance(notes, list):
            preview_panels = list((NotePreviewPanel(self, note), 0, wx.EXPAND) for note in notes)
            self.list_sizer.AddMany(preview_panels)
        else:
            preview_panel = NotePreviewPanel(self, notes)
            self.list_sizer.Prepend(preview_panel, flag=wx.EXPAND)

        self.SetupScrolling(scroll_x=False)

    def find(self, note_id):
        return self.FindWindow(NotePreviewPanel.get_name_by_note_id(note_id))

    def clear(self):
        self.list_sizer.Clear(True)

    def remove(self, note_id):
        panel = self.FindWindow(NotePreviewPanel.get_name_by_note_id(note_id))
        self.list_sizer.Detach(panel)
        panel.DestroyLater()

        if self.note_count == 0:
            self.show_empty_msg()
        self.SetupScrolling(scroll_x=False)

    def move(self, index, note_id):
        panel = self.FindWindow(NotePreviewPanel.get_name_by_note_id(note_id))
        self.list_sizer.Detach(panel)
        self.list_sizer.Insert(index, panel, flag=wx.EXPAND)
        self.SetupScrolling(scroll_x=False)

    @property
    def note_count(self):
        return self.list_sizer.GetItemCount()