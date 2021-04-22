import wx
from .todo_list import TodoList
from .todo_form_dialog import TodoFormDialog
from .todo_group_form_dialog import TodoGroupFormDialog
from models import Todo
from views import GenericMessageDialog
from pubsub import pub
from .popup_menu_mixin import PopupMenuMixin


class TodoPanel(wx.Panel, PopupMenuMixin):
    def __init__(self, parent):
        super().__init__(parent, style=wx.TE_PROCESS_ENTER|wx.BORDER_NONE)
        self.list = TodoList(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_sizer.Add(self.list, proportion=1, flag=wx.EXPAND|wx.ALL, border=5)
        self.__init_tool_bar()

        self.SetSizer(self.main_sizer)

        self.Bind(wx.EVT_BUTTON, self.add_todo, self.btn_add)
        self.Bind(wx.EVT_BUTTON, self.edit_todo, self.btn_edit)
        self.Bind(wx.EVT_BUTTON, self.delete_todo, self.btn_delete)
        self.Bind(wx.EVT_BUTTON, self.move_group, self.btn_move_group)
        self.Bind(wx.EVT_SHOW, self._on_show)

        self.note_id = None
        self._right_clicked_object = None

        self._list_right_click_menu_params = [
            dict(item=_("menu.edit"), handler=self._handle_edit_item),
            dict(item=_("menu.delete"), handler=self._handle_delete_item),
            dict(item=_("menu.priority"), sub_items=[
                dict(item='0', handler=self._set_item_priority, args=[0]),
                dict(item='1', handler=self._set_item_priority, args=[1]),
                dict(item='2', handler=self._set_item_priority, args=[2]),
            ])
        ]
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self._on_item_right_click, self.list)
        pub.subscribe(self._on_todo_checked, 'on.todo.checked')
        pub.subscribe(self._on_todo_preview, 'on.todo.preview')

        self.SetBackgroundColour(wx.WHITE)

    def _on_show(self, e):
        if e.IsShown():
            self.search_bar.SetFocus()

    def _on_todo_preview(self, model):
        self._show_edit_dialog(model)

    def _on_todo_checked(self, model, is_checked):
        if is_checked:
            model.set_finished()
        else:
            model.set_finished(False)
        pub.sendMessage('on.todo.change', note_id=self.note_id)
        self.list.update()

    def _handle_delete_item(self, e):
        self._show_delete_dialog(self._right_clicked_object)

    def _handle_edit_item(self, e):
        self._show_edit_dialog(self._right_clicked_object)

    def _set_item_priority(self, e, args):
        self._right_clicked_object.note_id = self.note_id
        self._right_clicked_object.priority = args[0]
        self._right_clicked_object.save()
        self.list.RefreshObject(self._right_clicked_object)

    def _on_item_right_click(self, e):
        self._right_clicked_object = self.list.find(e.GetIndex())
        self.setup_popup_menu(self._list_right_click_menu_params,self.list)
        self.show_popup_menu(e)

    def move_group(self, e):
        items = self.list.get_selected_objects()
        if not len(items):
            return False
        with TodoGroupFormDialog(self.note_id) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                Todo.set_group(items, dlg.get_group())
                self.list.update()

    def add_todo(self, e):
        with TodoFormDialog(note_id=self.note_id) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                todo = Todo.create(**self._get_dialog_detail(dlg))
                self.append(todo)
                pub.sendMessage('on.todo.change',note_id=self.note_id)

    def edit_todo(self, e):
        items = self.list.get_selected_objects()
        if not len(items):
            return False
        self._show_edit_dialog(items[0])

    def _get_dialog_detail(self, dlg):
        if dlg.get_is_finished():
            finished_at = dlg.get_finished_at()
        else:
            finished_at = None
        return dict(note_id=self.note_id, title=dlg.get_title(),content=dlg.get_content(), remark=dlg.get_remark(),
                    is_finished=dlg.get_is_finished(), finished_at=finished_at, group=dlg.get_group(),
                    priority=dlg.get_priority())

    def delete_todo(self, e):
        items = self.list.get_selected_objects()
        if len(items):
            self._show_delete_dialog(items)

    def __init_tool_bar(self):
        tool_sizer = wx.BoxSizer()

        self.search_bar = wx.SearchCtrl(self, size=(200,-1),style=wx.TE_PROCESS_ENTER)
        self.search_bar.ShowCancelButton(True)
        self.search_bar.SetHint(_("todo_panel.tool_bar_hint"))

        self.status_choice = wx.Choice(self, size=(120,-1), choices=[
            _("todo_panel.not_finished"), _("todo_panel.finished"), _("todo_panel.all")
        ])
        self.status_choice_param = ['not_finished', 'is_finished', 'all']

        self.btn_add = wx.Button(self, label=_("menu.add"))
        self.btn_edit = wx.Button(self, label=_("menu.edit"))
        self.btn_delete = wx.Button(self, label=_("menu.delete"))
        self.btn_move_group = wx.Button(self, label=_("menu.set_group"))

        tool_sizer.Add(self.search_bar)
        tool_sizer.AddStretchSpacer()
        tool_sizer.Add(self.status_choice)
        tool_sizer.AddSpacer(10)
        tool_sizer.Add(self.btn_add)
        tool_sizer.AddSpacer(10)
        tool_sizer.Add(self.btn_edit)
        tool_sizer.AddSpacer(10)
        tool_sizer.Add(self.btn_delete)
        tool_sizer.AddSpacer(10)
        tool_sizer.Add(self.btn_move_group)

        self.main_sizer.Add(tool_sizer, flag=wx.EXPAND|wx.ALL, border=5)
        self.Bind(wx.EVT_SEARCHCTRL_SEARCH_BTN, self.do_search, self.search_bar)
        self.Bind(wx.EVT_SEARCHCTRL_CANCEL_BTN, self.cancel_search, self.search_bar)
        self._is_search_cancelled = False

        self.Bind(wx.EVT_CHOICE, self.on_status_choice, self.status_choice)

    def on_status_choice(self, e):
        self.list.do_status_filter(self.status_choice_param[e.GetSelection()])

    def cancel_search(self, e):
        if not self._is_search_cancelled:
            self.list.reset_filter()
            self._is_search_cancelled = True

    def do_search(self, e):
        if not self.note_id:
            return False
        self.list.do_text_filter(self.search_bar.GetValue())
        self._is_search_cancelled = False

    def add_todos(self, note_id, todos):
        self.note_id = note_id
        self.search_bar.Clear()
        self._is_search_cancelled = False
        self._right_clicked_object = None
        self.list.text_filter.set_text('')
        self.list.set(todos)

        if self.IsShown():
            self.search_bar.SetFocus()

    def append(self, todo):
        self.list.add(todo)

    def empty(self):
        self.note_id = None
        self.search_bar.Clear()
        self.list.empty()

    def _show_delete_dialog(self, items):
        if not isinstance(items, list):
            items = [items]
        with GenericMessageDialog(_("todo_panel.delete_dialog_message"), _("todo_panel.delete_dialog_title")) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                ids = list(map(lambda item: item.id, items))
                Todo.delete_by_ids(ids)
                self.list.remove(items)
                pub.sendMessage('on.todo.change', note_id=self.note_id)

    def _show_edit_dialog(self, item):
        is_finished = item.is_finished
        with TodoFormDialog(item,note_id=self.note_id) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                item.update_instance(**self._get_dialog_detail(dlg))
                self.list.RefreshObject(item)
                self.list.RebuildGroups()
                if is_finished != item.is_finished:
                    pub.sendMessage('on.todo.change', note_id=self.note_id)
