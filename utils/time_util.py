from datetime import datetime
from datetime import date
from datetime import timedelta


class TimeUtil:
    @classmethod
    def is_today(cls, arg_time):
        return cls.get_datetime(arg_time).date() == datetime.now().date()

    @classmethod
    def is_yesterday(cls, arg_time):
        return cls.get_datetime(arg_time).date() == (datetime.now() - timedelta(days=1)).date()

    @classmethod
    def is_n_days_ago(cls, arg_time, n_day):
        return cls.get_datetime(arg_time).date() == (datetime.now() - timedelta(days=n_day)).date()

    @classmethod
    def get_pretty_time(cls, arg_time):
        pass

    @classmethod
    def get_datetime(cls, arg_time, **kwargs):
        if isinstance(arg_time, datetime):
            return arg_time
        if isinstance(arg_time, int):
            return datetime.fromtimestamp(arg_time)
        elif isinstance(arg_time, str):
            return datetime.strptime(arg_time, kwargs.pop('format','%Y-%m-%d %H:%M:%S'))
        elif isinstance(arg_time, date):
            return datetime.combine(arg_time, datetime.min.time())
        else:
            raise TypeError("unknown argument")
