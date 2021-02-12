"""
@File    : server.py
@Author  : CXJ
@Contact : github.com/WSWSCSJ
"""
import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError
from loguru import logger

from spider.jd_async_spider import JdAsyncSpider
"""
其他平台懒得写了,参照RequestVersion中的结构
"""
SpiderProcesses = {
    "item.jd": JdAsyncSpider,
    "detail.tmall": None,
    "item.taobao": None,
}

class PlatformPictureSpiderHandler(tornado.web.RequestHandler):

    async def post(self):
        """
        tornado运行时服务在一个事件循环中, 使用显式的await
        """
        self.set_header('Content-Type', 'application/json')
        try:
            url = self.get_body_argument("url")
        except MissingArgumentError:
            self.write({"code": 1, "msg": "无效的连接"})
        else:
            for mark, process in SpiderProcesses.items():
                if mark in url and process:
                    processor = process(url)
                    try:
                        await processor.explicit_run()
                    except Exception as e:
                        logger.error(e)
                        message = "解析失败,请重试" if isinstance(e, AttributeError) else e
                        self.write({"code": 1, "msg": str(message)})
                        return
                    else:
                        self.set_header('Content-Type', 'application/octet-stream')
                        self.set_header('Content-Disposition', 'attachment;filename=images.zip')
                        self.write(processor.zip_file)
                        return
        self.write({"code": 1, "msg": "无效的连接"})

def make_app():
    return tornado.web.Application([
        (r"/api/Pictures/", PlatformPictureSpiderHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(9999)
    tornado.ioloop.IOLoop.current().start()