from peewee import CharField, DateTimeField, BooleanField, SmallIntegerField, DeferredForeignKey
from .base_model import BaseModel
from datetime import datetime


class Todo(BaseModel):
    note = DeferredForeignKey("Note", null=False, on_delete='cascade', backref='todos', column_name="note_id")
    title = CharField(default="")
    content = CharField(default="")
    remark = CharField(default="")
    finished_at = DateTimeField()
    is_finished = BooleanField(default=False)
    group = CharField()
    priority = SmallIntegerField(default=0)

    def set_finished(self, is_finished=True):
        self.is_finished = is_finished
        if is_finished:
            self.finished_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        else:
            self.finished_at = None
        self.save()

    @classmethod
    def set_group(cls, todos, group_name):
        if not group_name:
            return False
        if isinstance(todos, list):
            for item in todos:
                item.group = group_name
                item.save()
        elif isinstance(todos, Todo):
            todos.group = group_name
            todos.save()
        else:
            raise RuntimeError('unexpected todos param')

    @classmethod
    def get_groups(cls, note_id=None):
        query = Todo.select(Todo.group).distinct()
        if note_id:
            query = query.where(Todo.note_id == note_id)
        groups = [item.group for item in query]
        if len(groups):
            return groups
        else:
            return [_("todo.no_group")]

    class Meta:
        table_name = "todos"
