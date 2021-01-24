"""
@Author: CXJ
"""
import os
import re
from io import BytesIO
from uuid import uuid4

import requests
from requests.exceptions import (
    ReadTimeout,
    ConnectTimeout,
    ProxyError,
    HTTPError,
)
import json
from loguru import logger

from Spider.spider.proxy import GlobalProxy
from Spider.spider.constants import Error, SpiderRuntimeError
from Spider.spider.ziptool import ByteZipFile, ZIP_DEFLATED


class Spider:

    __default_timeout = 10

    def __init__(self, url=None, proxy=None, headers={}, params={}, data={}):
        self.__url = url
        self.__headers = headers
        self.__params = params
        self.__data = data
        self.__payload = json.dumps(self.__data)
        self.__proxy = proxy
        self.__failure = None
        self.__fail_response = None
        self.__post_data_json = False
        self.__errors = []

    @property
    def post_data_json(self):
        return self.__post_data_json

    @post_data_json.setter
    def post_data_json(self, switch):
        self.__post_data_json = switch

    @property
    def url(self):
        if not hasattr(self, "_Spider__url"):
            return None
        return self.__url

    @url.setter
    def url(self, code):
        if not isinstance(code, str):
            raise ValueError("url must be string")
        self.__url = code

    @property
    def headers(self):
        if not hasattr(self, "_Spider__headers"):
            return {}
        return self.__headers

    @headers.setter
    def headers(self, headers_dict):
        if not isinstance(headers_dict, dict):
            raise ValueError("headers must be dict")
        self.__headers = headers_dict

    def set_headers(self, accept=None, accept_encoding=None, accept_language=None, content_length=None,
                    cookie=None, host=None, referer=None, user_agent=None, connection="keep-alive",
                    add_sec=False, headers_dict=None,
                    sec_fetch_dest="empty", sec_fetch_mode="cors", sec_fetch_site="same-origin"):
        if headers_dict is not None and not isinstance(headers_dict, dict):
            raise ValueError("headers_dict attribute must be dict")
        elif headers_dict is not None:
            self.__headers = headers_dict
        else:
            self.__headers = {
                'Accept': accept,
                'Accept-Encoding': accept_encoding,
                'Accept-Language': accept_language,
                'Content-Length': content_length,
                'Connection': connection,
                'Cookie': cookie,
                'Host': host,
                'Referer': referer,
                'User-Agent': user_agent,
            }
        if add_sec:
            self.__headers.update({
                'Sec-Fetch-Dest': sec_fetch_dest,
                'Sec-Fetch-Mode': sec_fetch_mode,
                'Sec-Fetch-Site': sec_fetch_site,
            })


    def update_headers(self, headers_args=None, **kwargs):
        if headers_args and not isinstance(headers_args, dict):
            raise ValueError("headers args must be set in dict")
        if headers_args:
            self.__headers.update(headers_args)
        if kwargs:
            self.__headers.update(kwargs)

    def del_headers_args(self, *args):
        for key in args:
            if isinstance(key, str) and key in self.__headers.keys():
                del self.__headers[key]

    @property
    def params(self):
        if not hasattr(self, "_Spider__params"):
            return None
        return self.__params

    @params.setter
    def params(self, params_dict):
        if not isinstance(params_dict, dict):
            raise ValueError("params must be dict")
        self.__params = params_dict

    def set_params(self, **kwargs):
        self.__params = kwargs

    def update_params(self, **kwargs):
        self.__params.update(kwargs)

    def del_params_args(self, *args):
        for key in args:
            if isinstance(key, str) and key in self.__params.keys():
                del self.__params[key]

    @params.deleter
    def params(self):
        self.__params = {}

    @property
    def data(self):
        if not hasattr(self, "_Spider__data"):
            return {}
        return self.__data

    def set_data(self, **kwargs):
        self.__data = kwargs

    @data.deleter
    def post_data(self):
        self.__data = {}

    def update_post_data(self, update_dict=None, **kwargs):
        if update_dict:
            self.__data.update(update_dict)
        if kwargs:
            self.__data.update(kwargs)

    @property
    def proxy(self):
        if not hasattr(self, "_Spider__proxy"):
            return {}
        return self.__proxy

    @proxy.setter
    def proxy(self, code):
        if not isinstance(code, dict):
            raise ValueError("proxy must be dict")
        self.__proxy = code

    @proxy.deleter
    def proxy(self):
        self.__proxy = None

    @property
    def failure(self):
        if not hasattr(self, "_Spider__failure"):
            return None
        return self.__failure

    @failure.deleter
    def failure(self):
        self.__failure = None

    @property
    def is_timeout(self):
        if isinstance(self.__failure, ConnectTimeout):
            return True
        return False

    @property
    def is_proxy_fail(self):
        return isinstance(self.__failure, ProxyError)

    @property
    def errors(self):
        if not hasattr(self, "_Spider__errors"):
            return []
        return self.__errors

    @errors.setter
    def errors(self, error_list):
        if not isinstance(error_list, list):
            raise ValueError("errors must be list")
        self.__errors = error_list

    @errors.deleter
    def errors(self):
        self.__errors = []

    def get_response(self, timeout=None, **kwargs):
        del self.failure
        try:
            response = requests.get(
                url=self.__url,
                headers=self.__headers,
                params=self.__params,
                timeout=timeout or Spider.__default_timeout,
                proxies=self.__proxy,
                **kwargs,
            )
        except Exception as e:
            self.__failure = e
            return None
        return response

    def post_response(self, timeout=None, **kwargs):
        del self.failure
        try:
            response = requests.post(
                url=self.__url,
                headers=self.__headers,
                params=self.__params,
                data=self.__data if not self.post_data_json else {},
                payload=self.__payload if self.post_data else None,
                timeout=timeout or Spider.__default_timeout,
                proxies=self.__proxy,
                **kwargs,
            )
        except Exception as e:
            self.__failure = e
            return None
        return response

    @staticmethod
    def multi_retry_response(retry=1, limit=1, errors=[], proxy=None, error_msg=None, **kwargs):
        proxies = {}
        if proxy:
            proxies = proxy.proxies
            if not proxies:
                raise SpiderRuntimeError(error_msg)
            logger.debug(kwargs)
            logger.debug(proxies)
        try:
            response = requests.request(**kwargs, proxies=proxies)
        except Exception as e:
            if retry < limit:
                for error in errors:
                    if isinstance(e, error):
                        logger.warning("retry cause by {}".format(str(e)))
                        return Spider.multi_retry_response(retry+1, limit, errors, **kwargs)
            return None
        else:
            return response

    def response(self, method, **kwargs):
        if method == 'post':
            return self.post_response(**kwargs)
        if method == 'get':
            return self.get_response(**kwargs)
        raise AttributeError('method error with {}'.format(method))

class PictureSpider:
    errors = [ConnectTimeout, ReadTimeout, ProxyError]
    proxy_generator = GlobalProxy

    def __init__(self):
        self.title = None
        self.main_picture_link = {}
        self.color_picture_link = []
        self.detail_picture_link = {}

    @staticmethod
    def between_filter(first_str, last_str, text):
        """
        Find string between first_str and last_str in text, don't contain first_str and last_str
        :return: String
        """
        pattern = re.compile(r'(?<={}).+?(?={})'.format(first_str, last_str))
        filter_text = ''.join(pattern.findall(text))
        return filter_text

    @staticmethod
    def request(**kwargs):
        return Spider.multi_retry_response(**kwargs, errors=PictureSpider.errors, error_msg=Error.EMPTY_PROXY)

    def to_local(self):
        s = os.sep
        if not self.title:
            self.title = "商品"
        zip_file = ByteZipFile(os.path.dirname(__file__) + s + str(uuid4()) + ".zip", "w")
        count = 1
        for value in self.main_picture_link.values():
            if value:
                zip_file.write_bytes(value, s.join([self.title, "主图", "{}.jpg".format(count)]))
                count += 1
        count = 1
        for link in self.color_picture_link:
            if link.get("content"):
                zip_file.write_bytes(link.get("content"), s.join([self.title, "颜色图", "{}.jpg".format(link.get("name"))]))
        for value in self.detail_picture_link.values():
            if value:
                zip_file.write_bytes(value, s.join([self.title, "详情图", "{}.jpg".format(str(count))]))
                count += 1
        zip_file.close()

    def to_bytes(self):
        s = os.sep
        if not self.title:
            self.title = "商品"
        zip_file_byte = BytesIO()
        zip_file = ByteZipFile(zip_file_byte, "w", ZIP_DEFLATED, allowZip64=False)
        count = 1
        for value in self.main_picture_link.values():
            if value:
                zip_file.write_bytes(value, s.join([self.title, "主图", "{}.jpg".format(count)]))
                count += 1
        count = 1
        for link in self.color_picture_link:
            if link.get("content"):
                zip_file.write_bytes(link.get("content"),
                                     s.join([self.title, "颜色图", "{}.jpg".format(link.get("name"))]))
        for value in self.detail_picture_link.values():
            if value:
                zip_file.write_bytes(value, s.join([self.title, "详情图", "{}.jpg".format(str(count))]))
                count += 1
        zip_file.close()
        zip_file_byte.seek(0)
        return zip_file_byte.read()

    def get_bytes(self, url):
        succeed, error = self.process(url)
        if succeed:
            return succeed, self.to_bytes()
        else:
            return succeed, error

    def process(self, **kwargs):
        """
        override get_main_picture_link
                 get_color_picture_link
                 get_detail_picture_link
        """
        pass

    def download(self, **kwargs):
        """
        override platform download method
        """
        pass

    def get_picture_link(self, **kwargs):
        pass

    def get_main_picture_link(self, **kwargs):
        pass

    def get_detail_picture_link(self, **kwargs):
        pass

    def get_color_picture_link(self, **kwargs):
        pass