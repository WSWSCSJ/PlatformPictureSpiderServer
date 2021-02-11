"""
@File    : base_async_spider.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
from io import BytesIO
from AsyncSpider.async_task import AsyncTask
from spider.ziptool import *
import os

class PictureAsyncSpider(AsyncTask):

    picture_link_request = {}
    detail_picture_link_request = {}
    download_request = {}

    def __init__(self, url,  **kwargs):
        super(PictureAsyncSpider, self).__init__(**kwargs)
        self.url = url
        self.sku = self.main_sku = self.title = None
        self.pictures = []
        self.zip_file = None

    def to_bytes(self):
        """
        获取图片链接二进制流,依照图片属性路径压缩至zipfile bytes stream
        """
        s = os.sep
        if not self.title:
            self.title = "商品"
        zip_file_byte = BytesIO()
        zip_file = ByteZipFile(zip_file_byte, "w", ZIP_DEFLATED, allowZip64=False)
        if not self.pictures:
            raise ValueError("base_async_spider.pictures empty")
        for picture in self.pictures:
            if picture["content"]:
                zip_file.write_bytes(
                    picture["content"], s.join([self.title, picture["folder"], picture["name"]])
                )
        zip_file.close()
        zip_file_byte.seek(0)
        self.zip_file = zip_file_byte.read()

    async def execute(self, **kwargs):
        pass

    def run(self, **kwargs):
        pass