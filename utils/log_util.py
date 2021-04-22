from datetime import datetime


class LogUtil:
    def __init__(self, log_prefix):
        self.prefix = log_prefix

    def log(self, message):
        print("{} {}: {}".format(datetime.now(), self.prefix, message))