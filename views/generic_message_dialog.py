import wx


class GenericMessageDialog(wx.MessageDialog):
    def __init__(self, message='',caption='',style=wx.OK|wx.CANCEL|wx.CANCEL_DEFAULT):
        super().__init__(None,message,caption,style=style)
        self.SetOKCancelLabels(_("dialog_ok"), _("dialog_cancel"))
