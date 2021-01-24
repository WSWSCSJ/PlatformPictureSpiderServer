EMPTY_BYTES = b''

class Error:
    EMPTY_RESPONSE = "访问链接失败"
    EMPTY_PROXY = "服务器代理异常"
    ATTRIBUTE_ERROR = "提取链接内容异常"

class SpiderRuntimeError(Exception):

    def __init__(self, msg=None):
        self.message = msg

    def __str__(self):
        return self.message or "Unknown Error"