"""
@File    : async_mysql.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
import asyncio
import aiomysql


class AsyncMySQL:
    ip = user = password = port \
        = database = connection = table \
        = columns = result = last_result \
        = max_storage = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def not_inited(self):
        return not (self.ip and self.user and self.password and self.port and self.database)

    async def init_connection(self):
        if self.not_inited:
            raise AttributeError("AsyncMySQLr arguments missing")
        self.connection = await aiomysql.connect(
            host=self.ip, user=self.user, password=self.password,
            db=self.database, port=int(self.port)
        )

    async def _select(self, query, *args):
        assert isinstance(query, str)
        async with self.connection.cursor() as cur:
            affect = await cur.execute(query, args)
        if affect > 0:
            _result = cur.fetchall()
            self.last_result, self.result = self.result, list(_result.result())
        else:
            raise IOError("query can not match any result")

    def select(self, query, *args):
        asyncio.get_event_loop().run_until_complete(self._select(query, *args))

    # TODO: override
    async def _insert(self, query, *args):
        pass

    def insert(self, query, *args):
        asyncio.get_event_loop().run_until_complete(self._insert(query, *args))

    # TODO: override
    async def _update(self, query, *args):
        pass

    def update(self, query, *args):
        asyncio.get_event_loop().run_until_complete(self._update(query, *args))

    # TODO: override
    async def _delete(self, query, *args):
        pass

    def delete(self, query, *args):
        asyncio.get_event_loop().run_until_complete(self._delete(query, *args))