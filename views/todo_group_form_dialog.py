import wx
from models import Todo


class TodoGroupFormDialog(wx.Dialog):
    def __init__(self, note_id):
        super().__init__(None,title=_("todo_group_form_dialog.title"))

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        group_list = Todo.get_groups(note_id)
        self.cb_group = wx.ComboBox(self, size=(300,-1), value=group_list[0], choices=group_list)

        self.main_sizer.AddSpacer(20)
        self.main_sizer.Add(self.cb_group,flag=wx.LEFT|wx.RIGHT,border=30)
        self.main_sizer.AddSpacer(20)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_ok = wx.Button(self, wx.ID_OK, _("dialog_ok"))
        btn_ok.SetDefault()
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL, _("dialog_cancel")))
        btn_sizer.AddButton(btn_ok)
        btn_sizer.Realize()

        self.main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)

        self.SetSizer(self.main_sizer)
        self.main_sizer.Fit(self)
        self.main_sizer.SetSizeHints(self)
        self.CenterOnScreen()

        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_OK)

    def get_group(self):
        return self.cb_group.GetValue().strip()

    def on_save(self, e):
        if self.get_group():
            self.EndModal(wx.ID_OK)
