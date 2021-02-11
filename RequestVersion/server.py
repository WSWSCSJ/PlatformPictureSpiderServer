import tornado.ioloop
import tornado.web
from tornado.web import MissingArgumentError

from loguru import logger

from Spider.jd_spider import JdSpider
from Spider.tm_spider import TmSpider
from Spider.tb_spider import TbSpider

SpiderProcesses = {
    "item.jd": JdSpider,
    "detail.tmall": TmSpider,
    "item.taobao": TbSpider,
}

class PlatformPictureSpiderHandler(tornado.web.RequestHandler):

    def post(self):
        self.set_header('Content-Type', 'application/json')
        try:
            url = self.get_body_argument("url")
        except MissingArgumentError:
            self.write({"code": 1, "msg": "无效的连接"})
        else:
            for mark, process in SpiderProcesses.items():
                if mark in url and process:
                    succeed, result = process().get_bytes(url)
                    if not succeed:
                        logger.error(result)
                        message = "解析失败,请重试" if isinstance(result, AttributeError) else result
                        self.write({"code": 1, "msg": message})
                        return
                    else:
                        self.set_header('Content-Type', 'application/octet-stream')
                        self.set_header('Content-Disposition', 'attachment;filename=images.zip')
                        self.write(result)
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