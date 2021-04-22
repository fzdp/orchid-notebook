import wx
import wx.aui as aui
from pubsub import pub
from views import NavPanel
from views import ListPanel
from views import TextEditor
from views import TodoPanel
from views import GenericMessageDialog
from views import NotebookFormDialog
from .notebook_choice_dialog import NotebookChoiceDialog
from .menu_bar_mixin import MenuBarMixin
from .status_bar import StatusBar
from services import NoteSearchService
from models import Notebook, Note
from config_manager import config
import i18n


class MainFrame(wx.Frame, MenuBarMixin):
    def __init__(self):
        super().__init__(None, title=config.get("APP.window_title"), size=(800, 600))
        self.aui_manager = aui.AuiManager(self,wx.aui.AUI_MGR_TRANSPARENT_HINT)

        self.nav_panel = NavPanel(self)
        self.list_panel = ListPanel(self)
        self.detail_panel = TextEditor(self)
        self.todo_panel = TodoPanel(self)

        self.status_bar = StatusBar(self)
        self.SetStatusBar(self.status_bar)

        self.aui_manager.AddPane(self.nav_panel, self.get_default_pane_info().Left().Row(0).BestSize(300,-1))
        self.aui_manager.AddPane(self.list_panel, self.get_default_pane_info().Left().Row(1).BestSize(250, -1).MinSize(150,-1))
        self.aui_manager.AddPane(self.detail_panel, self.get_default_pane_info().CenterPane().Position(0).BestSize(400,-1).MinSize(500,-1))
        self.aui_manager.AddPane(self.todo_panel, self.get_default_pane_info().CenterPane().Position(1).BestSize(400,-1).MinSize(500,-1))

        self.aui_manager.GetPane(self.todo_panel).Hide()
        self.aui_manager.GetArtProvider().SetMetric(wx.aui.AUI_DOCKART_SASH_SIZE, 1)
        self.aui_manager.Update()

        self.Maximize(True)
        self.register_listeners()

        self.build_menu_bar()

        self.current_note = None
        self.note_searcher = NoteSearchService()
        # tree root node is selected by default
        wx.CallAfter(self.detail_panel.Hide)

    def build_menu_bar(self):
        menu_item_params = [
            dict(item=_("menu_bar.edit"), sub_items=[
                dict(item=f'{_("menu_bar.cancel")}\tCtrl+Z',id=wx.ID_CANCEL),
                dict(item=f'{_("menu_bar.redo")}\tShift+Ctrl+X',id=wx.ID_REDO),
                dict(kind=wx.ITEM_SEPARATOR),
                dict(item=f'{_("menu_bar.cut")}\tCtrl+X',id=wx.ID_CUT),
                dict(item=f'{_("menu_bar.copy")}\tCtrl+C',id=wx.ID_COPY),
                dict(item=f'{_("menu_bar.paste")}\tCtrl+V',id=wx.ID_PASTE),
                dict(item=f'{_("menu_bar.select_all")}\tCtrl+A',id=wx.ID_SELECTALL)
            ]),
            dict(item=_("menu_bar.view"), sub_items=[
                dict(item=f'{_("menu_bar.toggle_task_panel")}\tCtrl+T', handler=self.on_toggle_todo_menu_click)
            ]),
            dict(item=_("menu_bar.change_lang"), sub_items=[
                dict(item=_("menu_bar.chinese"), handler=self.on_change_app_lang, args=['cn']),
                dict(item=_("menu_bar.english"), handler=self.on_change_app_lang, args=['en']),
            ])
        ]
        self.setup_menu_bar(menu_item_params)

    @staticmethod
    def get_default_pane_info():
        return aui.AuiPaneInfo().CaptionVisible(False).PaneBorder(False).CloseButton(False).PinButton(False).Gripper(False)

    def on_frame_closed(self, e):
        self.aui_manager.UnInit()
        del self.aui_manager
        self.Destroy()

    def register_listeners(self):
        self.Bind(wx.EVT_CLOSE, self.on_frame_closed)
        self.Bind(wx.EVT_ACTIVATE, self._on_activated)
        pub.subscribe(self.show_note_detail, 'note.show')
        pub.subscribe(self.on_note_move, 'on.note.move')
        pub.subscribe(self.create_note, 'note.new')
        pub.subscribe(self.save_note, 'note.save')
        pub.subscribe(self.list_note, 'note.list')
        pub.subscribe(self.search_note, 'on.note.search')
        pub.subscribe(self.on_note_delete, 'on.note.delete')
        pub.subscribe(self.create_notebook, 'notebook.create')
        pub.subscribe(self.delete_notebook,'notebook.delete')
        pub.subscribe(self.edit_notebook, 'notebook.edit')
        pub.subscribe(self.move_notebook, 'notebook.move')
        pub.subscribe(self.toggle_note_full_screen,'note.full_screen')
        pub.subscribe(self.sort_note, 'note.sort')
        pub.subscribe(self.on_note_copy,'on.note.copy')
        pub.subscribe(self.toggle_todo_panel, 'on.todo_status.click')
        pub.subscribe(self.on_notebook_root_click, 'notebook.list')
        pub.subscribe(self.delete_note_index, 'note.deleted.callback')
        pub.subscribe(self.update_note_index, 'note.updated.callback')
        pub.subscribe(self.add_note_index, 'note.created.callback')

    def _on_activated(self, _):
        self.detail_panel.webview.SetFocus()

    def on_notebook_root_click(self):
        self.current_note = None
        pub.sendMessage('on.note.hide')

    def on_toggle_todo_menu_click(self, _):
        self.toggle_todo_panel()

    def on_change_app_lang(self, __, args):
        config.set("APP.language", args[0])
        i18n.set("locale", args[0])
        self.UpdateWindowUI()

    def toggle_todo_panel(self):
        if not self.current_note:
            return False
        is_todo_panel_shown = self.aui_manager.GetPane(self.todo_panel).IsShown()
        self.aui_manager.GetPane(self.todo_panel).Show(not is_todo_panel_shown)
        self.aui_manager.GetPane(self.detail_panel).Show(is_todo_panel_shown)
        self.aui_manager.Update()

    def on_note_copy(self, note_id):
        copied_note = Note.find(note_id).copy()
        self.list_panel.add_new_note(copied_note)
        self.show_note(copied_note)
        self.nav_panel.note_tree.update_selected_notebook_count(1)

    def edit_notebook(self, notebook_id):
        notebook = Notebook.find(notebook_id)
        old_name = notebook.name
        with NotebookFormDialog(self, notebook) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                notebook.update_instance(name=dlg.get_name(),description=dlg.get_description())
                self.list_panel.update_header_title(dlg.get_name())
                if old_name != notebook.name:
                    self.nav_panel.note_tree.update_selected_notebook(notebook.name)

    def move_notebook(self, notebook_id):
        with NotebookChoiceDialog(self) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                notebook = Notebook.find(notebook_id)
                source_id, target_id = notebook.move(dlg.get_selected_notebook_id())
                if source_id != target_id:
                    self.nav_panel.note_tree.move_notebook_to(target_id, notebook)

    def sort_note(self, sort_field, sort_dir):
        note_ids = self.list_panel.note_ids
        notes = Note.find_by_ids(note_ids, order_field=sort_field, order_dir=sort_dir)
        self.list_panel.sort_notes(notes)

    def toggle_note_full_screen(self, enable):
        if enable:
            for component in [self.nav_panel,self.list_panel]:
                self.aui_manager.GetPane(component).Show(False)
            self.aui_manager.Update()
        else:
            for component in [self.nav_panel, self.list_panel]:
                self.aui_manager.GetPane(component).Show(True)
            self.aui_manager.Update()

    def delete_notebook(self, notebook_id):
        notebook = Notebook.find(notebook_id)
        caption = _("notebook.delete_dialog_title", v1=notebook.name)
        message = _("notebook.delete_dialog_message")
        with GenericMessageDialog(message,caption) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.nav_panel.note_tree.delete_selected_notebook()
                self.list_panel.empty()
                self.detail_panel.remove_note()
                self.todo_panel.empty()
                notebook.delete_instance()

    def create_notebook(self, parent_id):
        with NotebookFormDialog(self) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                notebook = Notebook.create(name=dlg.get_name(), description=dlg.get_description(), parent_id=parent_id)
                self.nav_panel.note_tree.append_notebook(notebook)

    def show_note_detail(self, note_id):
        if self.list_panel.selected_note_id != note_id:
            self.show_note(note_id)

    def show_note(self, note_param):
        if isinstance(note_param, int):
            note_id = note_param
            note = Note.find(note_id)
        elif isinstance(note_param, Note):
            note = note_param
            note_id = note.id
        else:
            raise('Unknown note_param')

        self.list_panel.highlight_note(note_id)
        self.detail_panel.add_note(note, self.list_panel.header_panel.query)
        self.todo_panel.add_todos(note.id, note.todos.all())

        self.current_note = note
        pub.sendMessage('on.note.show',note=note)

    def on_note_move(self, note_id):
        with NotebookChoiceDialog(self) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                target_notebook_id = dlg.get_selected_notebook_id()
                if target_notebook_id is None:
                    return
                source_id, target_id = Note.find(note_id).move(target_notebook_id)
                if source_id != target_id:
                    res = self.list_panel.delete_note(note_id)
                    if res:
                        self.show_note(res)
                    else:
                        self.todo_panel.empty()
                        self.detail_panel.remove_note()
                    self.nav_panel.note_tree.update_notebook_count(source_id, -1)
                    self.nav_panel.note_tree.update_notebook_count(target_id, 1)

    def on_note_delete(self, note_id):
        res = self.list_panel.delete_note(note_id)
        Note.find(note_id).delete_instance()
        if res:
            self.show_note(res)
        else:
            self.todo_panel.empty()
            self.detail_panel.remove_note()
            if self.detail_panel.IsShown():
                self.detail_panel.Hide()
        self.nav_panel.note_tree.update_selected_notebook_count(-1)

    def save_note(self, note_id, note_detail):
        note = Note.find(note_id)
        note.update(note_detail)
        self.detail_panel.update_timestamps()
        self.list_panel.update_selected_note(note)

    def create_note(self, notebook_id, is_markdown_enabled):
        if not notebook_id:
            return False
        if not self.detail_panel.IsShown():
            self.detail_panel.Show()
        note = Note.create(title='', notebook_id=notebook_id, is_markdown=is_markdown_enabled)
        self.list_panel.add_new_note(note)
        self.show_note(note)
        self.detail_panel.focus_title()
        self.nav_panel.note_tree.update_selected_notebook_count(1)
        wx.CallAfter(pub.sendMessage, "note.created.callback", note=note)

    def list_note(self, notebook_id):
        notebook = Notebook.find(notebook_id)
        query = notebook.notes.order_by(Note.updated_at.desc())
        notes = [n for n in query]
        self.list_panel.add_notes(notes, notebook)
        self._display_note_list(notes)

    def search_note(self, query, notebook_id):
        note_ids = self.note_searcher.search(query, notebook_id)
        notes = Note.find_by_ids(note_ids) if note_ids else []
        self.list_panel.add_notes(notes, is_from_search=True)
        self._display_note_list(notes)

    def _display_note_list(self, notes):
        if len(notes):
            note = notes[0]
            if not self.detail_panel.IsShown():
                self.detail_panel.Show()
            self.show_note(note)
        else:
            self.todo_panel.empty()
            self.detail_panel.remove_note()
            if self.detail_panel.IsShown():
                self.detail_panel.Hide()
            pub.sendMessage('on.note.hide')

    def delete_note_index(self, note_id):
        self.note_searcher.delete(note_id)

    def update_note_index(self, note):
        self.note_searcher.update(note)

    def add_note_index(self, note):
        self.note_searcher.add(note)
