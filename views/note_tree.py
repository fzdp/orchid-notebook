import wx
from models import Notebook
from .popup_menu_mixin import PopupMenuMixin
import wx.lib.agw.customtreectrl as customtreectrl
from pubsub import pub


class NoteTree(customtreectrl.CustomTreeCtrl, PopupMenuMixin):
    def __init__(self, parent):
        super().__init__(parent,style=wx.VSCROLL,agwStyle=customtreectrl.TR_HAS_BUTTONS|customtreectrl.TR_FULL_ROW_HIGHLIGHT|customtreectrl.TR_ELLIPSIZE_LONG_ITEMS|customtreectrl.TR_TOOLTIP_ON_LONG_ITEMS)
        self.root = self.AddRoot(_("note_tree.root_node"))
        self.tree_node_dict = {None: self.root}
        self._build_note_tree(None, self.root)

        self._init_ui()
        self._init_menu()
        self._init_event()

    @property
    def selected_notebook_id(self):
        node_data = self.GetSelection().GetData()
        if node_data:
            return node_data["id"]
        return None

    def _init_event(self):
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_item_selected)
        self.Bind(wx.EVT_SCROLLWIN, self._handle_scroll)
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._begin_drag)
        self.Bind(wx.EVT_TREE_END_DRAG, self._end_drag)

    def _init_menu(self):
        self.delete_notebook_item_id, self.edit_notebook_item_id, self.move_notebook_item_id = wx.NewIdRef(3)
        menu_item_params = [
            dict(item=_("notebook.new"), handler=self.on_create_notebook),
            dict(item=_("notebook.edit"), handler=self.on_edit_notebook, id=self.edit_notebook_item_id),
            dict(item=_("notebook.move"), handler=self.on_move_notebook, id=self.move_notebook_item_id),
            dict(item=_("notebook.delete"), handler=self.on_delete_notebook, id=self.delete_notebook_item_id)
        ]
        self.setup_popup_menu(menu_item_params, self)
        self.Bind(wx.EVT_CONTEXT_MENU, self.build_context_menu)

    def _init_ui(self):
        panel_font = self.GetFont()
        panel_font.SetPointSize(panel_font.GetPointSize() + 1)
        self.SetFont(panel_font)

        self.EnableSelectionGradient(False)
        self.EnableSelectionGradient(False)

        self.SetForegroundColour(wx.Colour(236, 236, 236))
        self.SetHilightFocusColour(wx.Colour(100, 100, 100))
        self.SetHilightNonFocusColour(wx.Colour(100, 100, 100))
        self.SetSpacing(20)

        self.SetBackgroundColour(wx.Colour(42,42,42))
        self.SetIndent(10)

        self.ShowScrollbars(wx.SHOW_SB_NEVER, wx.SHOW_SB_DEFAULT)
        self.ExpandAll()

    def _begin_drag(self, e):
        e.Allow()
        item = e.GetItem()

    def _end_drag(self, e):
        item = e.GetItem()
        if item:
            print(f'end drag: {item.GetData()}, {item.GetText()}')
        else:
            print('end drag: None')

    def _handle_scroll(self, e):
        if e.GetOrientation() == wx.VERTICAL:
            e.Skip()

    def _build_note_tree(self, parent_id, parent_item):
        child_notebooks = Notebook.select().where(Notebook.parent_id == parent_id)
        for note_book in child_notebooks:
            item = self.AppendItem(parent_item, '', data=self.get_notebook_info(note_book))
            self.set_item_text(item)
            self.tree_node_dict[note_book.id] = item
            self._build_note_tree(note_book.id, item)

    @staticmethod
    def get_notebook_info(notebook):
        return dict(id=notebook.id, name=notebook.name, count=notebook.notes.count())

    def append_notebook(self, notebook):
        data = self.get_notebook_info(notebook)
        item = self.AppendItem(self.GetSelection(), '', data=data)
        self.set_item_text(item, data)
        self.tree_node_dict[notebook.id] = item
        self.DoSelectItem(item)

    def move_notebook_to(self, parent_id, notebook):
        # remove old node
        old_item = self.tree_node_dict[notebook.id]
        self.Delete(old_item)

        # append new node
        parent_item = self.tree_node_dict[parent_id]
        data = self.get_notebook_info(notebook)
        item = self.AppendItem(parent_item, '', data=data)
        self.set_item_text(item, data)
        self.tree_node_dict[notebook.id] = item

    def on_create_notebook(self, _):
        pub.sendMessage('notebook.create', parent_id=self.selected_notebook_id)

    def on_delete_notebook(self, _):
        pub.sendMessage('notebook.delete',notebook_id=self.selected_notebook_id)

    def on_edit_notebook(self, _):
        pub.sendMessage('notebook.edit',notebook_id=self.selected_notebook_id)

    def on_move_notebook(self, _):
        pub.sendMessage('notebook.move',notebook_id=self.selected_notebook_id)

    def build_context_menu(self, e):
        self.show_popup_menu(e, set_position=False, callback=self.disable_context_menu)

    def disable_context_menu(self, menu):
        if self.GetChildrenCount(self.root) == 1:
            menu.Enable(self.delete_notebook_item_id, False)
        if self.GetSelection() == self.root:
            menu.Enable(self.delete_notebook_item_id, False)
            menu.Enable(self.edit_notebook_item_id, False)

    def set_item_text(self, item, item_data=None):
        item_data = item_data or item.GetData()
        self.SetItemText(item, '{}  {}'.format(item_data['name'], item_data['count']))

    def item_text_format(self, item_data):
        return '{}  {}'.format(item_data['name'], item_data['count'])

    def update_selected_notebook(self, new_name):
        current_selection = self.GetSelection()
        item_data = current_selection.GetData()
        item_data['name'] = new_name
        current_selection.SetData(item_data)
        self.set_item_text(current_selection, item_data=item_data)

    def update_notebook_count(self, note_book_id, changed_count):
        item = self.tree_node_dict.get(note_book_id, None)
        if item:
            data = item.GetData()
            data['count'] += changed_count
            item.SetData(data)
            self.set_item_text(item)

    def update_selected_notebook_count(self, changed_count):
        if self.selected_notebook_id:
            data = self.GetSelection().GetData()
            if changed_count == 0:
                data['count'] = 0
            else:
                data['count'] += changed_count
            self.GetSelection().SetData(data)
            self.set_item_text(self.GetSelection(), data)

    def delete_selected_notebook(self):
        if self.selected_notebook_id:
            self.Delete(self.GetSelection())
            self.tree_node_dict.pop(self.selected_notebook_id, None)

    def on_item_selected(self, evt):
        if self.selected_notebook_id:
            pub.sendMessage('note.list', notebook_id=self.selected_notebook_id)
        else:
            pub.sendMessage('notebook.list')
