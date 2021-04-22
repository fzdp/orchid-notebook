import os
import sys


class ApplicationUtil:
    @staticmethod
    def bundle_dir():
        return getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(os.path.dirname(__file__))))