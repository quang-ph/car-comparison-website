from flask import Flask, render_template, request, url_for
import requests
import json
from flask_paginate import Pagination, get_page_args
from os.path import join
import os

dirname = os.path.dirname(__file__)
CLASSIFY_PATH = join(dirname, '../car_scraper/label/car_labels.json')
with open(CLASSIFY_PATH, 'rt', encoding="utf8") as f:
    car_label = json.load(f)
brands = []
for brand in car_label['car']:
    brands.append(brand['brand'])
brands.sort()

app = Flask(__name__)
app.config["DEBUG"] = True
PER_PAGE = 16
cities = ["Cần Thơ", "Đà Nẵng", "Hải Phòng", "Hà Nội", "Hồ Chí Minh", "Bà Rịa - Vũng Tàu", "Bắc Giang", "Bắc Kạn", "Bạc Liêu", "Bắc Ninh", "Bến Tre", "Bình Định", "Bình Dương", "Bình Phước", "Bình Thuận", "Cà Mau", "Cao Bằng", "Đắk Lắk", "Đắk Nông", "Điện Biên", "Đồng Nai", "Đồng Tháp", "Gia Lai", "Hà Giang",
           "Hà Nam", "Hà Tĩnh", "Hải Dương", "Hậu Giang", "Hòa Bình", "Hưng Yên", "Khánh Hòa", "Kiên Giang", "Kon Tum", "Lai Châu", "Lâm Đồng", "Lạng Sơn", "Lào Cai", "Long An", "Nam Định", "Nghệ An", "Ninh Bình", "Ninh Thuận", "Phú Thọ", "Quảng Bình", "Quảng Nam", "Quảng Ngãi", "Quảng Ninh", "Quảng Trị",
          "Sóc Trăng", "Sơn La", "Tây Ninh", "Thái Bình", "Thái Nguyên", "Thanh Hóa", "Thừa Thiên Huế", "Tiền Giang", "Trà Vinh", "Tuyên Quang", "Vĩnh Long", "Vĩnh Phúc", "Yên Bái", "Phú Yên"]


def get_data(offset=0, per_page=12, data=[]):
    return data[offset: offset + per_page]


def url_for_other_page(page):
    args = request.view_args.copy()
    args['page'] = page
    return url_for(request.endpoint, **args)


app.jinja_env.globals['url_for_other_page'] = url_for_other_page


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/', methods=['GET'])
def homepage():
    return render_template('index.html', brands=brands, results=1)


@app.route('/groups', methods=['GET'])
def group_result():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    res_args = request.args
    car_name = res_args.get('name', '')
    car_brand = res_args.get('brand-selector', '')
    car_line = res_args.get('line-selector', '')
    new_car_name = car_brand + ' ' + car_line
    if car_name == '' and new_car_name == '':
        final_name = ''
    elif car_name != '':
        final_name = car_name
    else:
        final_name = new_car_name
    params = {
        "q": final_name,
    }
    total_response = requests.get('http://localhost:5000/api/v1/resources/groups/search', params=params)
    total_data = json.loads(total_response.text)['groups']
    total = len(total_data)
    pagination_data = get_data(offset=offset, per_page=12, data=total_data)
    pagination = Pagination(page=page, per_page=12, total=total, css_framework='bootstrap4')
    if len(total_data) > 0:
        return render_template('group_list.html', result=pagination_data, page=page, per_page=12, pagination=pagination, group_name=final_name)
    else:
        return render_template('index.html', result=0, brands=brands)


@app.route('/cars', methods=['GET'])
def car_result():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    args = request.args
    params = {
        "q": args.get('name'),
    }
    response = requests.get('http://localhost:5000/api/v1/resources/groups/info', params=params)
    identity_data = response.json()['info'][0]
    car_params = {
        'brand': identity_data['identity']['brand'],
        'line': identity_data['identity']['line'],
        'trim_level': identity_data['identity']['trim_level'],
        'sub_version': identity_data['identity']['sub_version'],
        'transmission': identity_data['transmission'],
        'engine_volume': identity_data['identity']['engine_volume'],
        "min_price": args.get('price-min', 0),
        "max_price": args.get('price-max', 1000000000),
        "year": args.get('year-filter', ''),
        "location": args.get('city-filter', ''),
        "status": args.get('status-option', ''),
    }
    print(car_params)
    total_response = requests.get('http://localhost:5000/api/v1/resources/cars/search', params=car_params)
    total_car_list = total_response.json()['car']
    total = len(total_car_list)
    pagination_data = get_data(offset=offset, per_page=10, data=total_car_list)
    pagination = Pagination(page=page, per_page=10, total=total, css_framework='bootstrap4')
    return render_template('price_list.html', info=identity_data,
                           car_list=pagination_data, page=page,
                           per_page=10, pagination=pagination, cities=cities)


@app.route('/all_cars', methods=['GET'])
def get_all_cars():
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')
    args = request.args
    name = args.get('name')
    brand_key = ''
    for brand in brands:
        if brand.lower() in name.lower():
            brand_key = brand
            break
    line_key = name.replace(brand_key.lower(), '').replace(brand_key, '').strip()
    car_params = {
        'brand': brand_key,
        'line': line_key,
        "min_price": args.get('price-min', 0),
        "max_price": args.get('price-max', 1000000000),
        "year": args.get('year-filter', ''),
        "location": args.get('city-filter', ''),
        "status": args.get('status-option', ''),
    }
    total_response = requests.get('http://localhost:5000/api/v1/resources/cars/search_all', params=car_params)
    total_car_list = total_response.json()['car']
    total = len(total_car_list)
    pagination_data = get_data(offset=offset, per_page=10, data=total_car_list)
    pagination = Pagination(page=page, per_page=10, total=total, css_framework='bootstrap4')
    return render_template('all_price_list.html',
                           car_list=pagination_data, page=page, key=name,
                           per_page=10, pagination=pagination, cities=cities)