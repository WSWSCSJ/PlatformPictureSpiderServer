from django.http import HttpResponse

from common.responses import *
from Spider.spider.jd_spider import JdSpider
from Spider.spider.tm_spider import TmSpider
from Spider.spider.tb_spider import TbSpider

SpiderProcesses = {
    "item.jd": JdSpider,
    "detail.tmall": TmSpider,
    "item.taobao": TbSpider,
}

class PictureSpiderView(APIView):
    permission_classes = ()

    def post(self, request):
        """
        如果使用get,传递的url中的参数会被视为请求的参数
        """
        url = request.data.get("url")
        if not url:
            return MESSAGE_RESPONSE(1, "无效的链接")
        for mark, process in SpiderProcesses.items():
            if mark in url and process:
                succeed, result = process().get_bytes(url)
                if not succeed:
                    logger.error(result)
                    if isinstance(result, AttributeError):
                        return MESSAGE_RESPONSE(1, "解析失败，请重试")
                    return MESSAGE_RESPONSE(1, result)
                response = HttpResponse(result)
                response["Content-Type"] = "application/octet-stream"
                response["Content-Disposition"] = "attachment;filename=images.zip"
                return response
        return MESSAGE_RESPONSE(1, "无效的链接")