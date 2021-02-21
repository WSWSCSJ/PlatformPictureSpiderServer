"""
@File    : async_task.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
@Description:
    简单的并发处理批量请求,不使用回调函数,override execute对请求结果进行处理
    case:
        async def process(self, **kwargs):
            pause = random.randint(2, 4)
            INFO(f"started pause {pause}")
            await asyncio.sleep(pause)
            response = await self.request(**kwargs)
            if response:
                INFO(f"response: {await response.text()}")


        def example():
            task = {
                "method": "GET", "url": "http://127.0.0.1:8000/test/",
                "timeout": 15
            }
            t = AsyncTask(process)
            t.set_tasks([task for _ in range(5)])
            t.run()


        example()
"""
import asyncio
from .async_spider import AsyncSpider, MethodType
from types import FunctionType

class AsyncTask(AsyncSpider):

    def __init__(self, execute_method=None, **kwargs):
        super(AsyncTask, self).__init__(**kwargs)
        self.__tasks = []
        if execute_method:
            assert isinstance(execute_method, FunctionType)
            self.execute = MethodType(execute_method, self)

    def set_tasks(self, tasks):
        assert isinstance(tasks, list)
        self.__tasks = tasks

    @property
    def empty(self):
        return not bool(self.__tasks)

    async def execute(self, **kwargs):
        raise NotImplementedError("override execute")

    async def async_process(self):
        if not self.empty:
            tasks = [asyncio.create_task(self.execute(**task)) for task in self.__tasks]
            await asyncio.gather(*tasks)