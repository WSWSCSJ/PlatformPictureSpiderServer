"""
@File    : jd_async_spider.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
@Description:
    使用 https://github.com/WSWSCSJ/AsyncSpiderFramework 框架
    重构 https://github.com/WSWSCSJ/PlatformPictureSpiderServer 项目
    只重构了JD平台的模块,其他的懒得写了
    相比较于旧项目使用request阻塞式的请求方式
    使用aiohttp并发得处理请求性能更好效率更高

    1、获取商品页面的document, 从document清洗提取关键字段和所有类型图片的链接
    2、在同一个事件循环中阻塞得发单个和多个并发请求

    单元测试用run()
    在tornado或其他异步框架中await explicit_run()

    async def __run(self, **kwargs):
        对一个商品链接的处理视作一次任务
        单个任务执行中分前置请求和获取图片二进制的并发请求,两者在代码逻辑上阻塞
        根据aiohttp https://docs.aiohttp.org/en/stable/client_quickstart.html#make-a-request
        文档建议,session的生命周期包含在一次任务中,避免重复实例化,请求共用一个session
        pass

    case:
        test = JdAsyncSpider("https://item.jd.com/10022464355924.html")
        test.run()
        with open("xxx.zip", "wb") as f:
            f.write(test.zip_file)
"""
import asyncio
import re
import time
from sys import stdout as out
from AiohttpVersion.AsyncSpider import ERROR

import aiohttp
from bs4 import BeautifulSoup
from AiohttpVersion.spider.base_async_spider import PictureAsyncSpider
from AiohttpVersion.spider.constants import *

class JdAsyncSpider(PictureAsyncSpider):

    picture_link_request = {
        "method": "GET", "timeout": 10, "limit": 10,
        "url": None, "verify_ssl": False,
        "headers": {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7',
            'upgrade-insecure-requests': '1',
            'Referer': 'https://item.jd.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
    }

    detail_picture_link_request = {
        "method": "GET", "timeout": 10, "limit": 10,
        "url": 'https://cd.jd.com/description/channel', "verify_ssl": False,
        "headers": {
            'Referer': None,
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        },
        "params": {
            'skuId': None,
            'mainSkuId': None,
            'cdn': 2,
            'callback': 'showdesc'
        }
    }

    download_request = {
        "method": "GET", "limit": 1, "timeout": 5,
        "url": None, "verify_ssl": False,
        "headers": {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
            'referer': None,
        }
    }

    async def download(self, picture):
        _ = self.download_request.copy()
        _["url"] = picture["link"]
        _["headers"]["referer"] = self.url
        response = await self.request(**_)
        if response:
            picture["content"] = await response.content.read()

    def get_main_picture_link(self, soup):
        count = 0
        for image_ul in soup.find_all('ul', {"class": "lh"}):
            for li in image_ul.find_all('li'):
                for img in li.find_all('img'):
                    count += 1
                    self.pictures.append(
                        {
                            "link": 'https:' + img.get('src').replace("50x64", "1026x1026"),
                            "folder": "主图",
                            "name": f"主图{count}.jpg",
                            "content": EMPTY_BYTES,
                        }
                    )

    def get_color_picture_link(self, soup):
        for div in soup.find_all('div', {"id": "choose-attrs"}):
            for img in div.find_all('img'):
                self.pictures.append(
                    {
                        "link": 'https:' + img.get('src').replace("60x76", "1026x1026"),
                        "folder": "颜色图",
                        "name": img.get('alt') + ".jpg",
                        "content": EMPTY_BYTES,
                    }
                )

    async def get_detail_picture_link(self):
        self.detail_picture_link_request["headers"]["Referer"] = 'https://item.jd.com/' + str(self.sku) + '.html'
        self.detail_picture_link_request["params"]["skuId"] = self.sku
        self.detail_picture_link_request["params"]["mainSkuId"] = self.main_sku
        response = await self.request(**self.detail_picture_link_request)
        if not response:
            out.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] get detail picture response error\n")
            raise SpiderRuntimeError(Error.EMPTY_RESPONSE)
        text = await response.text()
        json_data_str = str(text).replace(")'", "").replace("b'showdesc(", "")
        content = re.findall('"content":(.*)}', json_data_str)[0]
        soup = BeautifulSoup(content, 'lxml')
        count = 0
        for img in soup.find_all('img'):
            count += 1
            image_path = img.get('data-lazyload').replace('\\\\\"', "").\
                replace('http:', 'https:').replace(r'\"', "")
            if not image_path.startswith("https"):
                image_path = "https:" + image_path
            self.pictures.append(
                {
                    "link": image_path,
                    "folder": "详情图",
                    "name": f"详情图{count}.jpg",
                    "content": EMPTY_BYTES,
                }
            )

    async def __run(self):
        async with aiohttp.ClientSession() as session:
            self.session = session
            self.picture_link_request["url"] = self.url
            response = await self.request(**self.picture_link_request)
            if not response:
                ERROR(f"get picture link with empty response\n")
                raise SpiderRuntimeError(Error.EMPTY_RESPONSE)
            text = await response.text()
            soup = BeautifulSoup(text, "lxml")
            divs = soup.find(class_="parameter2 p-parameter-list")
            for li in divs.find_all('li'):
                if '货号' in li.text:
                    self.title = li.get('title')
                    break
            self.sku = re.findall("(\d+).html", self.url)[0]
            self.main_sku = re.findall("mainSkuId:'(\d+)',", text)[0]
            if not (self.sku and self.main_sku):
                ERROR(f"get sku and main sku error\n")
                raise SpiderRuntimeError(Error.ATTRIBUTE_ERROR)
            self.get_main_picture_link(soup)
            self.get_color_picture_link(soup)
            await self.get_detail_picture_link()
            tasks = [asyncio.create_task(self.download(picture)) for picture in self.pictures]
            await asyncio.gather(*tasks)
            self.to_bytes()

    def run(self):
        asyncio.get_event_loop().run_until_complete(self.__run())

    async def explicit_run(self):
        await self.__run()