import os
from os.path import join
import scrapy
from car_scraper.items import CarPost
from urllib.parse import urljoin, urlparse
import resource
import csv
import json
from car_scraper import formatters as fm
import pandas as pd
import datetime
import sys

dirname = os.path.dirname(__file__)
SELECTOR_PATH = join(dirname, '../selector/choxe.csv')
CLASSIFY_PATH = join(dirname, '../label/car_labels.json')
BASE_LINES_PATH = join(dirname, '../label/base_lines.csv')

resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))


def get_content(selector, response, index):
    if len(selector[index]) > 0:
        slt = response.xpath(selector[index])
        if slt:
            value = slt.extract()
            if len(value) > 0:
                return value
        else:
            return [""]
    else:
        return [""]


# load vào các label để phân loại xe
with open(CLASSIFY_PATH, 'rt', encoding="utf8") as f:
    car_label = json.load(f)

# Load label giúp tìm hãng xe từ tên xe
df = pd.read_csv(BASE_LINES_PATH)


class CarSpider(scrapy.Spider):
    name = 'carpost'
    download_delay = 1

    # load vào các selector
    with open(SELECTOR_PATH, 'rt', encoding="utf8") as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            for header, value in row.items():
                data.setdefault(header, list()).append(value)
        subject = data['subject']
        selector = data['selector']
        default_value = data['default']

    start_urls = [selector[0]]
    root_url = '{}://{}'.format(urlparse(start_urls[0]).scheme, urlparse(start_urls[0]).netloc)

    custom_settings = {
        'ITEM_PIPELINES': {
            'car_scraper.pipelines.CarPostPipeline': 300,
        },

        "SPLASH_URL": 'http://localhost:8050',
        "DOWNLOADER_MIDDLEWARES": {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy.contrib.downloadermiddleware.useragent.UserAgentMiddleware': None,
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
        },
        "USER_AGENT_CHOICES": [
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:23.0) Gecko/20100101 Firefox/23.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.62 Safari/537.36',
            'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; WOW64; Trident/6.0)',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.146 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome'
            '/33.0.1750.146 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64; rv:24.0) Gecko/20140205 Firefox/24.0 Iceweasel/24.3.0',
            'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0',
            'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:28.0) AppleWebKit/534.57.2 (KHTML, like Gecko)'
            ' Version/5.1.7 Safari/534.57.2',
        ],
        "DUPEFILTER_CLASS": 'scrapy_splash.SplashAwareDupeFilter',
        "HTTPCACHE_STORAGE": 'scrapy_splash.SplashAwareFSCacheStorage',
        "SPIDER_MIDDLEWARES": {
            'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
        },
        'RETRY_TIMES': 4,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 403, 404, 408],
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        car_links = response.xpath(self.selector[2]).extract()
        for link in car_links:
            if link.startswith('/') or link.startswith(self.root_url):
                link = urljoin(self.root_url, link)
                yield scrapy.Request(url=link, callback=self.parse_item)
        next_page = response.xpath(self.selector[1]).extract()
        for page in next_page:
            if page.startswith('/') or page.startswith(self.root_url):
                if not (self.default_value[10] == 'Banxehoi.com' and page == '/ban-xe/p101'):
                    page = urljoin(self.root_url, page)
                    yield scrapy.Request(url=page, callback=self.parse)

    def parse_item(self, response):
        car = CarPost()
        car['post_title'] = get_content(self.selector, response, 3)[0].strip()
        car['brand'] = get_content(self.selector, response, 4)[0].strip()
        car['line'] = get_content(self.selector, response, 5)[0].strip()
        car['version'] = get_content(self.selector, response, 6)[0].strip()
        car['year'] = get_content(self.selector, response, 7)[0].strip()
        car['price'] = fm.format_car_price(get_content(self.selector, response, 8)[0])
        car['status'] = get_content(self.selector, response, 9)[0].strip()
        car['source'] = self.default_value[10]
        car['location'] = get_content(self.selector, response, 11)[0].strip()
        car['seller_name'] = get_content(self.selector, response, 12)[0].strip()
        car['post_link'] = response.url
        car['transmission'] = get_content(self.selector, response, 14)[0].strip()
        car['images'] = get_content(self.selector, response, 15)
        car['color'] = get_content(self.selector, response, 16)[0].strip()
        car['car_type'] = get_content(self.selector, response, 17)[0].strip()
        car['classify'] = get_content(self.selector, response, 18)[0].strip()
        car['posted_time'] = fm.format_time(get_content(self.selector, response, 19)[0].strip().strip(" -"))

        fn_time = datetime.datetime.strptime(car['posted_time'], '%Y/%m/%d')
        cp_time = datetime.datetime(2018, 10, 1)
        if fn_time < cp_time and car['source'] != "Banxehoi.com":
            try:
                sys.exit("STOP CRAWLING")
            except Exception:
                pass

        car = fm.set_brand(dataframe=df, car=car)
        car = fm.set_label(car, car_label=car_label)
        if car is not None:
            car = fm.format_data(car, self.root_url)
            car['name'] = car['brand'] + " " + car['line'] + " " + car['engine_volume'] + " " + car['trim_level'] + " " + car['transmission'] + " " + car['sub_version']
            car['name'] = car['name'].replace(" other", "")
            yield car
