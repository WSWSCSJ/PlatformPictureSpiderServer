"""
@File    : async_proxy.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
@Description:
    ProxyStorage: 封装List的代理IP暂存对象
    高并发AsyncSpider避免频繁进行数据IO
"""
from AsyncSpider.async_mysql import AsyncMySQL
from AsyncSpider.logger import log

MAX_STORAGE = 50

DATABASE = {
    "ip": 'your database ip',
    "user": "your user name",
    "password": "your password",
    "port": "3306",
    "database": "your database",
    "table": "your table",
    "columns": "target column",
}

SQL_STATEMENT = f"select {DATABASE['columns']} from {DATABASE['table']} limit {MAX_STORAGE}"

class ProxyStorage:

    def __init__(self):
        self.proxies = []
        self.limit = MAX_STORAGE

    def insert(self, value):
        self.proxies.append(value)
        if len(self.proxies) > self.limit:
            del self.proxies[0]

    @property
    def empty(self):
        return len(self.proxies) == 0

    @property
    def proxy(self):
        if self.proxies:
            return self.proxies.pop()
        raise ValueError("fetch proxy error")

class AsyncProxy(AsyncMySQL):

    def __init__(self, **kwargs):
        super(AsyncProxy, self).__init__(**kwargs)
        self.__storage = ProxyStorage()
        if self.max_storage:
            self.__storage.limit = self.max_storage
        self.sql_statement = \
            f"select {self.columns} from {self.table} limit {self.max_storage or MAX_STORAGE}"

    async def fill(self):
        if not self.__storage.empty:
            return True
        try:
            await self._select(self.sql_statement)
        except Exception as e:
            log(f"fill storage from select error with {e}")
            return False
        else:
            for _ in self.result:
                self.__storage.insert(_[0])

    async def proxy(self):
        if self.__storage.empty:
            await self.fill()
        return self.__storage.proxy