import traceback
import re
from bs4 import BeautifulSoup
from loguru import logger

from Spider.spider import PictureSpider
from Spider.constants import *


class JdSpider(PictureSpider):

    def __init__(self):
        super(JdSpider, self).__init__()
        self.sku = None
        self.main_sku = None

    def get_picture_link(self, url):
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-encoding': 'gzip, deflate, br',
            'accept-language': 'en,zh;q=0.9,zh-TW;q=0.8,en-US;q=0.7',
            'upgrade-insecure-requests': '1',
            'Referer': 'https://item.jd.com/',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'
        }
        response = self.request(
            limit=10, url=url, method="GET", timeout=10,
            headers=headers, proxy=self.proxy_generator, verify=False
        )
        if not response:
            logger.error("get picture link with empty response")
            raise SpiderRuntimeError(Error.EMPTY_RESPONSE)
        soup = BeautifulSoup(response.content, "lxml")
        divs = soup.find(class_="parameter2 p-parameter-list")
        for li in divs.find_all('li'):
            if '货号' in li.text:
                self.title = li.get('title')
                break
        self.sku = re.findall("(\d+).html", url)[0]
        self.main_sku = re.findall("mainSkuId:'(\d+)',", response.text)[0]
        if not (self.sku and self.main_sku):
            logger.error("get sku and main sku error")
            raise SpiderRuntimeError(Error.ATTRIBUTE_ERROR)
        self.get_main_picture_link(soup)
        self.get_color_picture_link(soup)
        self.get_detail_picture_link(self.sku, self.main_sku)

    def get_main_picture_link(self, soup):
        for image_ul in soup.find_all('ul', {"class": "lh"}):
            for li in image_ul.find_all('li'):
                for img in li.find_all('img'):
                    image_path = 'https:' + img.get('src').replace("50x64", "1026x1026")
                    self.main_picture_link[image_path] = EMPTY_BYTES

    def get_color_picture_link(self, soup):
        for div in soup.find_all('div', {"id": "choose-attrs"}):
            for img in div.find_all('img'):
                tmp = {
                    'name': img.get('alt'),
                    'url': 'https:' + img.get('src').replace("60x76", "1026x1026"),
                    'content': EMPTY_BYTES,
                }
                self.color_picture_link.append(tmp)

    def get_detail_picture_link(self, sku, main_sku):
        url = 'https://cd.jd.com/description/channel'
        headers = {
            'Referer': 'https://item.jd.com/' + str(sku) + '.html',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36',
        }
        params = {
            'skuId': sku,
            'mainSkuId': main_sku,
            'cdn': 2,
            'callback': 'showdesc'
        }
        response = self.request(
            limit=10, url=url, method="GET", timeout=3, params=params,
            headers=headers, proxy=self.proxy_generator
        )
        if not response:
            logger.error("get detail picture response error")
            raise SpiderRuntimeError(Error.EMPTY_RESPONSE)
        json_data_str = str(response.content).replace(")'", "").replace("b'showdesc(", "")
        content = re.findall('"content":(.*)}', json_data_str)[0]
        soup = BeautifulSoup(content, 'lxml')
        for img in soup.find_all('img'):
            image_path = img.get('data-lazyload').replace('\\\\\"', "").replace('http:', 'https:')
            self.detail_picture_link[image_path] = EMPTY_BYTES

    def download(self, url, link):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
            'referer': url,
        }
        if 'http:' not in link and 'https:' not in link:
            link = 'https:' + link
        response = self.request(
            limit=10, url=link, method="GET", timeout=5,
            headers=headers, proxy=self.proxy_generator
        )
        return response.content if hasattr(response, "content") else response

    def process(self, url):
        try:
            self.get_picture_link(url)
        except Exception as e:
            logger.error(traceback.format_exc())
            return False, e
        for link in self.main_picture_link.keys():
            self.main_picture_link[link] = self.download(url, link)
        for link in self.color_picture_link:
            link["content"] = self.download(url, link.get("url"))
        for link in self.detail_picture_link.keys():
            self.detail_picture_link[link] = self.download(url, link)
        return True, None