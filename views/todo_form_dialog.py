import wx
import wx.adv
from datetime import datetime
from models import Todo


class TodoFormDialog(wx.Dialog):
    def __init__(self, todo=None, note_id=None):
        self.todo = todo
        title = _("todo_form_dialog.title_edit") if todo else _("todo_form_dialog.title_creation")
        super().__init__(None, title=title)

        st_title = wx.StaticText(self, label=_("todo.title"))
        self.tc_title = wx.TextCtrl(self)

        st_content = wx.StaticText(self, label=_("todo.content"))
        self.tc_content = wx.TextCtrl(self,style=wx.TE_MULTILINE, size=(400,120))

        st_finished_time = wx.StaticText(self, label=_("todo.finished_at"))
        self.dp_finished = wx.adv.DatePickerCtrl(self, size=(150,-1))
        self.tp_finished = wx.adv.TimePickerCtrl(self, size=(100,-1),style=wx.adv.TP_DEFAULT)

        finished_sizer = wx.BoxSizer()
        finished_sizer.Add(self.dp_finished)
        finished_sizer.AddSpacer(20)
        finished_sizer.Add(self.tp_finished)

        st_remark = wx.StaticText(self, label=_("todo.remark"))
        self.tc_remark = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=(400,120))

        st_group = wx.StaticText(self, label=_("todo.group"))
        group_list = Todo.get_groups(note_id)
        self.cb_group = wx.ComboBox(self, value=group_list[0], choices=group_list, size=(200,-1))

        st_priority = wx.StaticText(self, label=_("todo.priority"))
        self.cb_priority = wx.ComboBox(self, choices=['0', '1', '2'], size=(200, -1))

        st_is_finished = wx.StaticText(self, label=_("todo.is_finished"))
        self.ck_is_finished = wx.CheckBox(self)

        main_sizer = wx.BoxSizer(wx.VERTICAL)

        g_sizer = wx.FlexGridSizer(cols=2, gap=(10,10))
        g_sizer.AddGrowableCol(1)

        g_sizer.Add(st_title)
        g_sizer.Add(self.tc_title, flag=wx.EXPAND)

        g_sizer.Add(st_content)
        g_sizer.Add(self.tc_content, flag=wx.EXPAND)

        g_sizer.Add(st_remark)
        g_sizer.Add(self.tc_remark, flag=wx.EXPAND)

        g_sizer.Add(st_group)
        g_sizer.Add(self.cb_group)

        g_sizer.Add(st_priority)
        g_sizer.Add(self.cb_priority)

        g_sizer.Add(st_is_finished)
        g_sizer.Add(self.ck_is_finished)

        g_sizer.Add(st_finished_time)
        g_sizer.Add(finished_sizer)

        # 隐藏
        self.g_sizer = g_sizer
        self.st_finished_time = st_finished_time
        self.finished_sizer = finished_sizer

        if not self.todo or not self.todo.is_finished:
            self._show_finished_time_ctrl(False)

        main_sizer.Add(g_sizer, flag=wx.EXPAND|wx.ALL, border=10)
        # main_sizer.Add(wx.StaticLine(self), flag=wx.EXPAND|wx.BOTTOM, border=15)

        btn_sizer = wx.StdDialogButtonSizer()
        btn_sizer.AddButton(wx.Button(self, wx.ID_CANCEL, _("dialog_cancel")))
        btn_ok = wx.Button(self, wx.ID_OK, _("dialog_ok"))
        btn_ok.SetDefault()
        btn_sizer.AddButton(btn_ok)
        btn_sizer.Realize()

        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, border=5)

        self.SetSizer(main_sizer)
        main_sizer.Fit(self)
        main_sizer.SetSizeHints(self)

        self.main_sizer = main_sizer

        self.CenterOnScreen()

        self.set_values()
        self.bind_events()

    def _show_finished_time_ctrl(self, is_show):
        self.g_sizer.Show(12, is_show)
        self.g_sizer.Show(13, is_show)

    def get_title(self):
        return self.tc_title.GetValue().strip()

    def get_content(self):
        return self.tc_content.GetValue().strip()

    def get_remark(self):
        return self.tc_remark.GetValue().strip()

    def get_group(self):
        return self.cb_group.GetValue().strip()

    def get_priority(self):
        return int(self.cb_priority.GetValue().strip())

    def get_finished_at(self):
        return self.dp_finished.GetValue().Format('%F') + ' ' + self.tp_finished.GetValue().Format('%T')

    def get_is_finished(self):
        return self.ck_is_finished.GetValue()

    def set_title(self, val):
        if val:
            self.tc_title.SetValue(val)

    def set_content(self, val):
        if not val:
            return False
        self.tc_content.SetValue(val)

    def set_remark(self, val):
        if not val:
            return False
        self.tc_remark.SetValue(val)

    def set_group(self, val):
        if not val:
            return False
        self.cb_group.SetValue(val)

    def set_priority(self, val):
        self.cb_priority.SetValue(str(val))

    # current_time: datetime
    def set_finished_at(self, current_time):
        if not current_time:
            return False
        self.dp_finished.SetValue(wx.DateTime(current_time.day, current_time.month - 1, current_time.year))
        self.tp_finished.SetTime(current_time.hour, current_time.minute, current_time.second)

    def set_is_finished(self, val):
        self.ck_is_finished.SetValue(val)

    def set_values(self):
        if not self.todo:
            self.set_finished_at(datetime.now())
            self.tc_title.SetFocus()
            return None

        if self.todo.finished_at:
            if type(self.todo.finished_at) == str:
                current_time = datetime.strptime(self.todo.finished_at, '%Y-%m-%d %H:%M:%S')
            else:
                current_time = self.todo.finished_at
        else:
            current_time = datetime.now()
        self.set_title(self.todo.title)
        self.set_content(self.todo.content)
        self.set_remark(self.todo.remark)
        self.set_group(self.todo.group)
        self.set_priority(self.todo.priority)
        self.set_finished_at(current_time)
        self.set_is_finished(self.todo.is_finished)

        self.tc_title.SelectAll()

    def bind_events(self):
        self.Bind(wx.EVT_BUTTON, self.on_save, id=wx.ID_OK)
        self.Bind(wx.EVT_CHECKBOX, self.on_check, self.ck_is_finished)

    def on_check(self, e):
        if e.IsChecked():
            self._show_finished_time_ctrl(True)
        else:
            self._show_finished_time_ctrl(False)

        self.main_sizer.Fit(self)
        self.main_sizer.SetSizeHints(self)

    def on_save(self, e):
        if self.get_title():
            self.EndModal(wx.ID_OK)