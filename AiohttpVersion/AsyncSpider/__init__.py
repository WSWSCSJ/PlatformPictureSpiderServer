"""
@File    : __init__.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
import os
from .async_mysql import AsyncMySQL
from .async_proxy import AsyncProxy
from .async_spider import AsyncSpider
from .async_task import AsyncTask
from .logger import INFO, DEBUG, WARNING, ERROR
from .configure import Configure

__all__ = [
    'AsyncMySQL', 'AsyncProxy', 'AsyncSpider', 'AsyncTask',
    'PROJECT_DIR_PATH', 'INFO', 'WARNING', 'DEBUG', 'ERROR',
    'DATABASE', 'get_configure'
]

PROJECT_DIR_PATH = os.path.dirname(__file__)

DATABASE = {
    "ip": 'your database ip',
    "user": "your user name",
    "password": "your password",
    "port": "3306",
    "database": "your database",
    "table": "your table",
    "columns": "target column",
}

def get_configure(configure_file_path: str) -> dict:
    if not os.path.exists(configure_file_path):
        raise FileNotFoundError(f'{configure_file_path} doesnt exists')
    __config = Configure()
    __config.read(configure_file_path)
    return __config.to_dict()