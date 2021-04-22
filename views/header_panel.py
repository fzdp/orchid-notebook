import wx
from .generic_bitmap_button import GenericBitmapButton
from .popup_menu_mixin import PopupMenuMixin
from pubsub import pub
from models import Notebook


class HeaderPanel(wx.Panel, PopupMenuMixin):
    def __init__(self, parent, notebook_id=-1, notebook_name='', note_count=0):
        super().__init__(parent, style=wx.BORDER_NONE)
        self.SetBackgroundColour("#ebebeb")

        self.notebook_id = notebook_id
        self.notebook_name = notebook_name
        self.note_count = note_count
        self.query = None

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.st_notebook_name = wx.StaticText(self, label=notebook_name)

        self.note_action_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.st_note_count = wx.StaticText(self, label=_("header_panel.note_count", v1=note_count))
        self.note_action_sizer.Add(self.st_note_count)

        self.note_action_sizer.AddStretchSpacer()

        self.btn_display_order_options = GenericBitmapButton(self, 'sort')
        self.note_action_sizer.Add(self.btn_display_order_options)

        self.btn_display_notebook_options = GenericBitmapButton(self, 'more')
        self.note_action_sizer.Add(self.btn_display_notebook_options,flag=wx.LEFT,border=10)

        self.main_sizer.Add(self.st_notebook_name, flag=wx.ALL, border=10)
        self.main_sizer.Add(self.note_action_sizer, flag=wx.ALL|wx.EXPAND, border=10)

        self.search_bar = wx.SearchCtrl(self,style=wx.TE_PROCESS_ENTER)
        self.search_bar.ShowCancelButton(True)

        search_menu = wx.Menu()
        search_menu.AppendCheckItem(wx.ID_ANY, _("header_panel.search_all_notebooks"))
        self.is_global_search = False
        self.search_bar.SetMenu(search_menu)

        self.search_bar.SetHint(_("header_panel.search_current_notebook"))

        self.main_sizer.Add(self.search_bar, flag=wx.EXPAND|wx.LEFT|wx.RIGHT, border=8)
        self.main_sizer.AddSpacer(10)

        self.Bind(wx.EVT_TEXT, self._on_search_change, self.search_bar)
        self.Bind(wx.EVT_MENU, self._on_search_menu_click)

        self.SetSizer(self.main_sizer)

        self.menu_delete_notebook_id = wx.NewIdRef()
        menu_item_params = [
            dict(item=_("notebook.rename"), handler=self.on_rename_notebook),
            dict(item=_("notebook.move"), handler=self.on_move_notebook),
            dict(item=_("notebook.delete"), handler=self.on_delete_notebook, id=self.menu_delete_notebook_id)
        ]
        self.setup_popup_menu(menu_item_params, self.btn_display_notebook_options, wx.EVT_BUTTON, callback=self.notebook_action_menu_callback)

        self.selected_order_option_id = wx.NewIdRef()
        menu_item_params = [
            dict(item=_("header_panel.sort_by_updated"), sub_items=[
                dict(item=_("header_panel.time_desc"), handler=self.on_sort_note,args=['updated_at','desc'],kind=wx.ITEM_CHECK,id=self.selected_order_option_id),
                dict(item=_("header_panel.time_asc"), handler=self.on_sort_note,args=['updated_at','asc'],kind=wx.ITEM_CHECK)
            ]),
            dict(item=_("header_panel.sort_by_created"), sub_items=[
                dict(item=_("header_panel.time_desc"), handler=self.on_sort_note,args=['created_at','desc'],kind=wx.ITEM_CHECK),
                dict(item=_("header_panel.time_asc"), handler=self.on_sort_note,args=['created_at','asc'],kind=wx.ITEM_CHECK)
            ]),
            dict(item=_("header_panel.sort_by_title"), sub_items=[
                dict(item=_("header_panel.title_desc"), handler=self.on_sort_note,args=['title','desc'],kind=wx.ITEM_CHECK),
                dict(item=_("header_panel.title_asc"), handler=self.on_sort_note,args=['title','asc'],kind=wx.ITEM_CHECK)
            ])
        ]
        self.setup_popup_menu(menu_item_params, self.btn_display_order_options, wx.EVT_BUTTON, lambda menu: menu.Check(self.selected_order_option_id, True))

    def _on_search_menu_click(self, e):
        menu = wx.Menu()
        self.is_global_search = e.IsChecked()
        menu.AppendCheckItem(wx.ID_ANY, _("header_panel.search_all_notebooks")).Check(self.is_global_search)
        self.search_bar.SetMenu(menu)

        if self.is_global_search:
            self.search_bar.SetHint(_("header_panel.search_all_notebooks"))
        else:
            self.search_bar.SetHint(_("header_panel.search_current_notebook"))

    def _on_search_change(self, e):
        self.query = e.GetString().strip()
        # todo debounce query event
        if self.query:
            notebook_id = None if self.is_global_search else self.notebook_id
            pub.sendMessage('on.note.search', query=self.query, notebook_id=notebook_id)
        else:
            pub.sendMessage('note.list', notebook_id=self.notebook_id)

    def clear_search(self):
        self.search_bar.ChangeValue('')
        self.query = None

    def notebook_action_menu_callback(self, menu):
        if Notebook.count() == 1:
            menu.Enable(self.menu_delete_notebook_id, False)

    def update_note_count(self, count, is_search_result=False):
        self.note_count = count
        if is_search_result:
            note_count = _("header_panel.global_search_result", v1=count) if self.is_global_search else _("header_panel.current_search_result", v1=count)
            self.st_note_count.SetLabel(note_count)
        else:
            self.st_note_count.SetLabel(_("header_panel.note_count", v1=count))

    def update(self, notebook_id, notebook_name):
        self.notebook_id = notebook_id
        self.notebook_name = notebook_name
        self.update_title(notebook_name)

    def empty(self):
        self.notebook_id = 0
        self.notebook_name = ''
        self.note_count = 0
        self.query = None

    def update_title(self, title):
        self.notebook_name = title
        self.st_notebook_name.SetLabel(title)

    def on_delete_notebook(self, e):
        pub.sendMessage('notebook.delete', notebook_id=self.notebook_id)

    def on_rename_notebook(self, e):
        pub.sendMessage('notebook.edit', notebook_id=self.notebook_id)

    def on_move_notebook(self, _):
        pub.sendMessage('notebook.move', notebook_id=self.notebook_id)

    def on_sort_note(self, e, args):
        self.selected_order_option_id = e.GetId()
        pub.sendMessage('note.sort',sort_field=args[0],sort_dir=args[1])
