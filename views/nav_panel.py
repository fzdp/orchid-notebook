import wx
from pubsub import pub
from .note_tree import NoteTree
import images


class NavPanel(wx.Panel):
    DEFAULT_BACKGROUND_COLOUR = "#2a2a2a"

    def __init__(self, parent):
        super().__init__(parent, size=(200,-1))

        v_sizer = wx.BoxSizer(wx.VERTICAL)

        self.btn_new_note = wx.Button(self,style=wx.NO_BORDER)
        self.btn_new_note.SetBitmap(images.create_note.GetBitmap())
        self.btn_new_note.SetBackgroundColour(self.DEFAULT_BACKGROUND_COLOUR)
        self.btn_new_note.SetLabelMarkup(f'<span fgcolor="white" weight="bold" size="large">{_("note.new")}</span>')

        v_sizer.Add(self.btn_new_note, flag=wx.ALIGN_CENTER|wx.TOP, border=40)
        v_sizer.AddSpacer(20)

        self.note_tree = NoteTree(self)

        v_sizer.Add(self.note_tree, proportion=1,flag=wx.EXPAND)
        self.SetSizer(v_sizer)

        self.SetBackgroundColour(self.DEFAULT_BACKGROUND_COLOUR)

        self.Bind(wx.EVT_BUTTON, lambda _ : pub.sendMessage('note.new',notebook_id=self.note_tree.selected_notebook_id,is_markdown_enabled=False), self.btn_new_note)
