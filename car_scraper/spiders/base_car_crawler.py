import os
from os.path import join
import scrapy
import csv
from car_scraper.items import BaseCarInfo
import pandas as pd
import json
from car_scraper import formatters as fm

dirname = os.path.dirname(__file__)
SELECTOR_PATH = join(dirname, '../base_selector/vnbasecar.csv')
BASE_LINES_PATH = join(dirname, '../label/base_lines.csv')
CLASSIFY_PATH = join(dirname, '../label/car_labels.json')

# Load label giúp tìm hãng xe từ tên xe
df = pd.read_csv(BASE_LINES_PATH)

# load vào các label để phân loại xe
with open(CLASSIFY_PATH, 'rt', encoding="utf8") as f:
    car_label = json.load(f)


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


class BaseSpider(scrapy.Spider):
    name = 'basecar'
    download_delay = 0.05

    # Load các selector dùng cho parsing dữ liệu
    with open(SELECTOR_PATH, 'rt', encoding="utf8") as f:
        reader = csv.DictReader(f)
        data = {}
        for row in reader:
            for header, value in row.items():
                data.setdefault(header, list()).append(value)
        subject = data['subject']
        selector = data['selector']
        default_value = data['default']

    start_urls = []
    default_url = 'https://vnexpress.net/interactive/2016/bang-gia-xe/'
    for i in range(200, 2500):
        start_urls.append(default_url + str(i) + '.html')

    custom_settings = {
        'ITEM_PIPELINES': {
            'car_scraper.pipelines.BasePipeline': 300,
        },
    }

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        car_info = BaseCarInfo()
        car_info['identity'] = fm.format_base_identity(df, car_label, get_content(self.selector, response, 0)[0].strip())
        car_info['dimension'] = fm.format_base_dimension(get_content(self.selector, response, 1)[0].strip())
        car_info['fuel_tank'] = fm.format_base_string(get_content(self.selector, response, 2)[0].strip())
        car_info['engine'] = get_content(self.selector, response, 3)[0].strip()
        car_info['engine_power'] = fm.format_base_string(get_content(self.selector, response, 4)[0].strip())
        car_info['momentum'] = fm.format_base_string(get_content(self.selector, response, 5)[0].strip())
        car_info['ground_clearance'] = fm.format_base_string(get_content(self.selector, response, 6)[0].strip())
        car_info['minimum_turn_diameter'] = fm.format_base_string(get_content(self.selector, response, 7)[0].strip())
        car_info['style'] = get_content(self.selector, response, 9)[0].strip()
        car_info['transmission'] = fm.format_base_transmission(get_content(self.selector, response, 10)[0].strip())
        car_info['fuel_consumption'] = fm.format_base_string(get_content(self.selector, response, 11)[0].strip())
        car_info['price'] = fm.format_base_price(get_content(self.selector, response, 12)[0].strip())
        car_info['image'] = get_content(self.selector, response, 13)[0].strip()
        yield car_info
