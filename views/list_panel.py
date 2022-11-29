import wx
from .header_panel import HeaderPanel
from .note_list_panel import NoteListPanel
from pubsub import pub
import re


class ListPanel(wx.Panel):
    def __init__(self, parent):
        super().__init__(parent, size=(200,-1), style=wx.BORDER_NONE)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)

        self.header_panel = HeaderPanel(self)
        self.main_sizer.Add(self.header_panel,flag=wx.EXPAND)

        self.note_list_panel = NoteListPanel(self)
        self.main_sizer.Add(self.note_list_panel,flag=wx.EXPAND,proportion=1)

        self.SetSizer(self.main_sizer)

        self.selected_note_id = None
        self.note_ids = []

        pub.subscribe(self._update_selected_note_content, 'on.note_content.change')
        pub.subscribe(self._update_selected_note_title, 'on.note_title.change')

    def highlight_note(self, note_id):
        if self.selected_note_id != note_id:
            if self.selected_note_id:
                self.note_list_panel.find(self.selected_note_id).undo_highlight()
            self.selected_note_id = note_id
            self.note_list_panel.find(note_id).highlight()

    def update_selected_note(self, note):
        if self.selected_note_id:
            self.note_list_panel.find(self.selected_note_id).refresh(note)

    def _update_selected_note_title(self, title, updated_at):
        panel = self.note_list_panel.find(self.selected_note_id)
        panel.update_title(title)
        panel.update_time(updated_at)

        if self.note_ids[0] != self.selected_note_id:
            self._move_note_to(0, self.selected_note_id)

    def _update_selected_note_content(self, content, updated_at):
        panel = self.note_list_panel.find(self.selected_note_id)
        panel.update_time(updated_at)

        if self.note_ids[0] != self.selected_note_id:
            self._move_note_to(0, self.selected_note_id)

    def _move_note_to(self, index, note_id):
        self.note_ids.remove(note_id)
        self.note_ids.insert(index, note_id)
        self.note_list_panel.move(index, note_id)

    def add_new_note(self, note):
        self.note_list_panel.add(note)
        self.note_ids.insert(0, note.id)
        self.header_panel.update_note_count(self.header_panel.note_count + 1)

    def sort_notes(self, sorted_notes):
        selected_note_id = self.selected_note_id
        self.note_list_panel.clear()
        self.selected_note_id = None

        self.note_ids = list(map(lambda note: note.id, sorted_notes))
        self.note_list_panel.add(sorted_notes)
        self.highlight_note(selected_note_id)

    def empty(self):
        self.header_panel.empty()
        self.note_list_panel.clear()
        self.note_ids = []
        self.selected_note_id = None

    def update_header_title(self, title):
        self.header_panel.update_title(title)

    def delete_note(self, note_id):
        self.note_list_panel.remove(note_id)
        self.header_panel.update_note_count(self.header_panel.note_count - 1)

        self.selected_note_id = None
        current_note_id_index = self.note_ids.index(note_id)

        if len(self.note_ids) == 1:
            self.note_ids.remove(note_id)
            return None

        if len(self.note_ids) > current_note_id_index + 1:
            next_note_id = self.note_ids[current_note_id_index + 1]
        else:
            next_note_id = self.note_ids[current_note_id_index - 1]
        self.note_ids.remove(note_id)
        # return next or previous note
        return next_note_id

    def add_notes(self, notes, notebook=None, **kwargs):
        self.note_list_panel.clear()
        self.selected_note_id = None
        if len(notes):
            self.note_ids = list(map(lambda note: note.id, notes))
        else:
            self.note_ids = []
        self.note_list_panel.add(notes)

        if kwargs.pop('is_from_search', False):
            self.header_panel.update_note_count(len(notes), True)
        else:
            self.header_panel.clear_search()
            self.header_panel.update(notebook.id, notebook.name)
            self.header_panel.update_note_count(len(notes))

    def update_note_count(self):
        self.header_panel.update_note_count(self.note_list_panel.note_count)
