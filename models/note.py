from .base_model import BaseModel
from peewee import CharField, ForeignKeyField
from .notebook import Notebook
from .todo import Todo
import uuid
import os
import re
import shutil
from config_manager import config
from pubsub import pub

NOTE_DIR = config.get("PATH.notes_dir")


def generate_uuid():
    dir_uuid = str(uuid.uuid4())
    note_dir = os.path.join(NOTE_DIR, dir_uuid)
    os.makedirs(note_dir, exist_ok=True)
    open(os.path.join(note_dir, 'content.html'), 'w').close()
    open(os.path.join(note_dir, 'snippet.txt'), 'w').close()
    return dir_uuid


class Note(BaseModel):
    notebook = ForeignKeyField(Notebook, on_delete='cascade', backref='notes')
    local_uuid = CharField(default=generate_uuid)
    title = CharField(default="")

    @property
    def note_dir(self):
        return os.path.join(NOTE_DIR, self.local_uuid)

    @property
    def content_file(self):
        return os.path.join(self.note_dir, 'content.html')

    @property
    def snippet_file(self):
        return os.path.join(self.note_dir, 'snippet.txt')

    @property
    def snippet(self):
        with open(self.snippet_file, 'r', encoding='utf-8') as reader:
            return reader.read()

    @property
    def content(self):
        with open(self.content_file, 'r', encoding='utf-8') as reader:
            return reader.read()

    def set_content(self, content):
        with open(self.content_file, 'w', encoding='utf-8') as writer:
            writer.write(content)
        with open(self.snippet_file, 'w', encoding='utf-8') as writer:
            writer.write(re.sub(r'<.*?>','', content))
        self.save()
        pub.sendMessage("note.updated.callback", note=self)

    def copy(self):
        with self._meta.database.atomic():
            note_dict = self.to_dict(excluded_columns=["id", "updated_at", "created_at"])
            note_dict["title"] = _("note.copied_title", v1=self.title)
            new_note = Note.create(**note_dict)
            model_list = []
            for todo in self.todos:
                model_list.append(todo.to_dict(excluded_columns=["id", "updated_at", "created_at"]))
            Todo.insert_many(model_list).execute()
        return new_note

    def move(self, notebook_id):
        old_notebook_id = self.notebook_id
        if old_notebook_id != notebook_id:
            self.notebook_id = notebook_id
            self.save()
        return old_notebook_id, notebook_id

    def get_todo_status(self):
        todos = [t for t in self.todos]
        finished_todos = list(filter(lambda item: item.is_finished, todos))
        return dict(total=len(todos), finished=len(finished_todos))

    def delete_instance(self, *args, **kwargs):
        shutil.rmtree(self.note_dir, ignore_errors=True)
        super().delete_instance(*args, **kwargs)
        pub.sendMessage("note.deleted.callback", note_id=self.id)

    class Meta:
        table_name = "notes"