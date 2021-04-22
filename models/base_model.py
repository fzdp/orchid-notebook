from peewee import Model, DateTimeField, SqliteDatabase, ModelSelect
from config_manager import config
import datetime


def all(self):
    return [item for item in self]


setattr(ModelSelect, 'all', all)


class BaseModel(Model):
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)

    def save(self, *args, **kwargs):
        self.updated_at = datetime.datetime.now()
        return super().save(*args, **kwargs)

    def update_instance(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.save()

    @classmethod
    def count(cls):
        return cls.select().count()

    @classmethod
    def find(cls, id):
        return cls.get_by_id(id)

    @classmethod
    def all(cls):
        return [item for item in cls.select()]

    @classmethod
    def find_by_ids(cls, *ids, **kwargs):
        if isinstance(ids[0], list):
            ids = ids[0]
        order_field = getattr(cls, kwargs.pop('order_field', 'updated_at'))
        if kwargs.pop('order_dir', 'desc').lower() == "desc":
            order_field = order_field.desc()
        query = cls.select().where(cls._meta.primary_key.in_(ids)).order_by(order_field)
        return [item for item in query]

    @classmethod
    def delete_by_ids(cls, *ids):
        if isinstance(ids[0], list):
            ids = ids[0]
        cls.delete().where(cls._meta.primary_key.in_(ids)).execute()

    @classmethod
    def first(cls, n=1):
        return cls.select().first(n=n)

    @classmethod
    def columns(cls):
        return list(cls._meta.columns.keys())

    def to_dict(self, excluded_columns=None):
        db_columns = self.columns()
        if excluded_columns:
            for col in excluded_columns:
                db_columns.remove(col)
        db_values = [getattr(self, col) for col in db_columns]
        return dict(zip(db_columns, db_values))

    class Meta:
        database = SqliteDatabase(config.get("PATH.db_file"), pragmas={'foreign_keys': 1})