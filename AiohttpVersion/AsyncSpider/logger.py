"""
@File    : logger.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
from datetime import datetime
import inspect


def info(message):
    Logger.log(level='INFO   ', message=message)


def debug(message):
    Logger.log(level='DEBUG  ', message=message)


def warning(message):
    Logger.log(level='WARNING', message=message)


def error(message):
    Logger.log(level='ERROR  ', message=message)


class Logger:

    @staticmethod
    def __get_stack_frame_info():
        return inspect.stack()[3]

    @classmethod
    def log(cls, level, message):
        stack = cls.__get_stack_frame_info()
        filename = stack.filename
        filename = filename.split('/')[-1] if '/' in filename else filename.split('\\')[-1]
        print(
            f'[{datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}] {level} |'
            f'{filename}:{stack.frame.f_code.co_name}:{stack.lineno} | {message}'
        )


INFO = info
DEBUG = debug
WARNING = warning
ERROR = error