import traceback
from bs4 import BeautifulSoup

from lxml import etree
from loguru import logger

from Spider.spider.spider import PictureSpider
from Spider.spider.constants import *


class TbSpider(PictureSpider):

    def __init__(self):
        super(TbSpider, self).__init__()
        self.cookie = "your tmp cookie"

    def get_picture_link(self, url):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36',
        }
        response = self.request(
            limit=10, url=url, method="GET", timeout=5,
            headers=headers, proxy=self.proxy_generator
        )
        if not response:
            logger.error("get taobao first response error")
            raise SpiderRuntimeError(Error.EMPTY_RESPONSE)
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup.find_all('script'):
            if 'descUrl  ' in script.text:
                desc_url = 'https://descnew.' + \
                           self.between_filter("'//dscnew.", "'//descnew.", script.text).split("'")[0]
                headers = {
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                    'Accept-encoding': 'gzip, deflate, br',
                    'Accept-language': 'zh-CN,zh;q=0.9',
                    'Cache-control': 'max-age=0',
                    'Sec-fetch-mode': 'navigate',
                    'Sec-fetch-site': 'none',
                    'Sec-fetch-user': '?1',
                    'Upgrade-insecure-requests': '1',
                    'Cookie': self.cookie,
                    'User-Agent': 'User-Agent:Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
                }
                response = self.request(
                    limit=10, url=desc_url, headers=headers,
                    timeout=5, method="GET", proxy=self.proxy_generator
                )
                if not response:
                    logger.error("get taobao second response error")
                else:
                    try:
                        tmp_soup = BeautifulSoup(response.content, "html.parser")
                        for img in tmp_soup.find_all('img'):
                            self.detail_picture_link[img["src"]] = EMPTY_BYTES
                    except Exception as e:
                        logger.error(e)
                break
        body_html = etree.HTML(response.text)
        try:
            self.title = body_html.xpath('//*[@id="J_Title"]/h3/text()')[0]
        except:
            self.title = body_html.xpath('//*[@id="J_DetailMeta"]//div[@class="tb-detail-hd"]/h1/text()')[0]
        self.get_main_picture_link(body_html)
        self.get_color_picture_link(body_html)

    def get_main_picture_link(self, html):
        img_xpath = html.xpath('//*[@id="J_UlThumb"]/li//a/img')
        for path in img_xpath:
            try:
                image_path = "https:" + path.attrib["data-src"].replace("50x50", "800x800")
            except:
                image_path = "https:" + path.attrib["src"].replace("50x50", "800x800")
            self.main_picture_link[image_path] = EMPTY_BYTES

    def get_color_picture_link(self, html):
        lis = html.xpath('//ul[@data-property="颜色"]/li')
        for li in lis:
            for a in li.xpath("a"):
                tmp = {
                    "name": a.xpath("span/text()"),
                    "url": 'https:' + a.xpath('@style')[0][15:-19].replace("30x30", "800x800"),
                    "content": EMPTY_BYTES,
                }
                self.color_picture_link.append(tmp)

    def download(self, url):
        if 'http:' not in url and 'https:' not in url:
            url = 'https:' + url
        response = self.request(
            url=url, limit=10, method="GET", timeout=5,
            proxy=self.proxy_generator
        )
        return response.content if hasattr(response, "content") else response

    def process(self, url):
        try:
            self.get_picture_link(url)
        except Exception as e:
            logger.error(traceback.format_exc())
            return False, e
        for link in self.main_picture_link.keys():
            self.main_picture_link[link] = self.download(link)
        for link in self.color_picture_link:
            link["content"] = self.download(link.get("url"))
        for link in self.detail_picture_link.keys():
            self.detail_picture_link[link] = self.download(link)
        return True, None