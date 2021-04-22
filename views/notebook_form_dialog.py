import wx


class NotebookFormDialog(wx.Dialog):
    def __init__(self, parent, notebook=None):

        self.notebook = notebook
        if self.notebook:
            super().__init__(parent, title=_("notebook_form_dialog.title_edit"))
        else:
            super().__init__(parent, title=_("notebook_form_dialog.title_creation"))

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        g_sizer = wx.FlexGridSizer(cols=2,gap=(10,10))
        g_sizer.AddGrowableCol(1)

        g_sizer.Add(wx.StaticText(self, label=_("notebook.name")))
        self.tc_name = wx.TextCtrl(self, size=(400,-1))
        g_sizer.Add(self.tc_name, flag=wx.EXPAND)

        g_sizer.Add(wx.StaticText(self, label=_("notebook.description")))
        self.tc_description = wx.TextCtrl(self, size=(400,160),style=wx.TE_MULTILINE)
        g_sizer.Add(self.tc_description, flag=wx.EXPAND)

        main_sizer.Add(g_sizer, flag=wx.EXPAND|wx.ALL, border=10)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL, _("dialog_cancel")))
        button = wx.Button(self, wx.ID_OK, _("dialog_ok"))
        btn_sizer.AddButton(button)
        button.SetDefault()
        btn_sizer.Realize()

        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)

        if self.notebook:
            self.tc_name.SetValue(self.notebook.name)
            self.tc_description.SetValue(self.notebook.description)

            self.tc_name.SelectAll()

        self.SetSizer(main_sizer)
        main_sizer.Fit(self)

        self.CenterOnScreen()

        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_OK)

    def get_name(self):
        return self.tc_name.GetValue().strip()

    def get_description(self):
        return self.tc_description.GetValue().strip()

    def on_save(self, e):
        if self.get_name():
            self.EndModal(wx.ID_OK)

