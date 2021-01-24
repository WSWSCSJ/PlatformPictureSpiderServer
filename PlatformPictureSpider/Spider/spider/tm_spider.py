import traceback
from bs4 import BeautifulSoup

from loguru import logger

from Spider.spider.spider import PictureSpider
from Spider.spider.constants import *


class TmSpider(PictureSpider):

    def __init__(self):
        super(TmSpider, self).__init__()
        self.cookie = "your tmp cookie"
        
    def get_picture_link(self, url):
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Host': 'detail.tmall.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
            'Accept-Language': 'zh-cn',
            'Referer': 'https://list.tmall.com/search_product.htm?q=%BB%A8%BB%A8%B9%AB%D7%D3&type=p&vmarket=&spm=875.7931836%2FB.a2227oh.d100&from=mallfp..pc_1_searchbutton',
            'Connection': 'keep-alive',
            'Cookie': self.cookie,
        }
        response = self.request(
            limit=10, url=url, method="GET", headers=headers,
            timeout=5, proxy=self.proxy_generator
        )
        if not response:
            logger.error("get tmall first response error")
            raise SpiderRuntimeError(Error.EMPTY_RESPONSE)
        soup = BeautifulSoup(response.content, "html.parser")
        for script in soup.find_all('script'):
            if 'TShop.Setup(' in script.text:
                desc_url = 'https:' + self.between_filter('"httpsDescUrl":"', '","fetchDcUrl', script.text)
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
                    url=desc_url, headers=headers, timeout=5,
                    proxy=self.proxy_generator, limit=10
                )
                if not response:
                    logger.error("get tmall second response error")
                else:
                    try:
                        tmp_soup = BeautifulSoup(response.text, "html.parser")
                        for img in tmp_soup.find_all('img'):
                            self.detail_picture_link[img["src"]] = EMPTY_BYTES
                    except Exception as e:
                        logger.error(e)
                break
        for li in soup.find('ul', {"id": "J_AttrUL"}).find_all("li"):
            if "货号" in li.text:
                self.title = li.text[4:]
            elif "款号" in li.text:
                self.title = li.text[4:]
        self.get_main_picture_link(soup)
        self.get_color_picture_link(soup)

    def get_main_picture_link(self, soup):
        for image_ul in soup.find_all('ul', {"id": "J_UlThumb"}):
            for li in image_ul.find_all('li'):
                for img in li.find_all('img'):
                    image_path = 'https:' + img['src'].replace(img['src'].split('_')[-1], "")[:-1]
                    self.main_picture_link[image_path] = EMPTY_BYTES

    def get_color_picture_link(self, soup):
        for li in soup.find('div', {"class": "tb-sku"}).find_all('dl')[1].find_all('li'):
            for a in li.find_all("a"):
                tmp = {
                    "name": a.find("span").text,
                    "url": "https" + a.get("style").replace("background:url(","").replace(") center no-repeat;","").replace('40','800'),
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