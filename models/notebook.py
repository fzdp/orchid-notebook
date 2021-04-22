from peewee import CharField, ForeignKeyField
from .base_model import BaseModel
import shutil


class Notebook(BaseModel):
    parent = ForeignKeyField('self', null=True, on_delete='cascade', backref='notebooks')
    name = CharField(default="")
    description = CharField(default="")

    def delete_instance(self, *args, **kwargs):
        for note in self.notes:
            shutil.rmtree(note.note_dir, ignore_errors=True)
        super().delete_instance(*args, **kwargs)

    def move(self, parent_notebook_id):
        old_parent_id = self.parent_id
        if old_parent_id != parent_notebook_id:
            self.parent_id = parent_notebook_id
            self.save()
        return old_parent_id, parent_notebook_id

    class Meta:
        table_name = "notebooks"