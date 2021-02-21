"""
@File    : async_spider.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
import asyncio
from types import MethodType
import aiohttp
from .async_proxy import AsyncProxy, DATABASE
from traceback import format_exc
from .logger import DEBUG, ERROR, WARNING

class AsyncSpider:

    def __init__(self, process_method=None, use_proxy=False):
        self.use_proxy = use_proxy
        self.session = self.proxy_generator = None
        if process_method:
            self.async_process = MethodType(process_method, self)

    async def init_proxy(self):
        self.proxy_generator = AsyncProxy(**DATABASE)
        await self.proxy_generator.init_connection()

    async def request(self, retry=1, limit=1, debug=False, **kwargs):
        """
        :param retry: current retry times
        :param limit: max retry times
        :param kwargs: request arguments
        :param debug: log out kwargs
        :return: None or aiohttp.ClientResponse
        """
        if debug:
            DEBUG(f"kwargs: {kwargs}")
        response = None
        try:
            response = await self.session.request(**kwargs)
        except Exception as e:
            ERROR(f"ClientSession request error with {e}")
            if debug:
                print(format_exc())
            if retry < limit:
                WARNING(f"retry {retry}/{limit}")
                return await self.request(retry+1, limit, **kwargs)
        finally:
            return response

    async def request_with_proxy(self, retry=1, limit=1, debug=False, **kwargs):
        """
        no matter kwargs contains proxy or not, set proxy equals AsyncProxy().proxy
        cause aiohttp.ClientSession only support http proxy
        :param retry: current retry times
        :param limit: max retry times
        :param debug: log out kwargs
        :param kwargs: request arguments
        :return: None or aiohttp.ClientResponse
        """
        kwargs["proxy"] = await self.proxy_generator.proxy()
        response = await self.request(debug=debug, **kwargs)
        if not response and retry < limit:
            return await self.request_with_proxy(retry+1, limit, **kwargs)
        return response

    async def __process(self, **kwargs):
        """
        aiohttp.ClientSession cant init in regular function
        """
        if self.use_proxy:
            await self.init_proxy()
        async with aiohttp.ClientSession() as session:
            self.session = session
            await self.async_process(**kwargs)

    async def async_process(self, **kwargs):
        raise NotImplementedError("write your own process")

    def run(self, **kwargs):
        asyncio.run(self.__process(**kwargs))