from flask import request, jsonify
from app.webappl import app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from app.webappl import app as frontend
import json
from flask_pymongo import PyMongo, pymongo
from os.path import join
import os

dirname = os.path.dirname(__file__)
CLASSIFY_PATH = join(dirname, '../car_scraper/label/car_labels.json')
with open(CLASSIFY_PATH, 'rt', encoding="utf8") as f:
    car_label = json.load(f)

app.config["DEBUG"] = True
app.config['MONGO_DBNAME'] = 'sosanhgiaxe'
app.config['MONGO_URI'] = "mongodb://localhost:27017/sosanhgiaxe"
mongo = PyMongo(app)


def convert_price(price_text):
    if len(price_text) > 9:
        result = price_text[0:-9] + " tỷ " + str(int(float(price_text[-9:-6]))) + " triệu"
    elif len(price_text) > 6:
        result = str(int(float(price_text[0:-6]))) + " triệu"
    return result


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found in Careno.</p>", 404


@app.route('/api/test', methods=['GET'])
def test():
    return "Indexes created"


@app.route('/api/v1/resources/groups/search', methods=['GET'])
def search_group():
    base_cars = mongo.db.basecar
    query_parameters = request.args
    car_name = query_parameters.get('q').strip()
    if car_name == '':
        groups_cursor = base_cars.find({}, {'_id': 0})
    else:
        groups_cursor = base_cars.find({"$text": {'$search': '\"' + car_name + '\"'}},
                                       {'_id': 0}).collation({'locale': 'en', 'strength': 2})
    groups = [doc for doc in groups_cursor]
    return jsonify({'groups': groups})


@app.route('/api/v1/resources/groups/info', methods=['GET'])
def get_group_info():
    base_cars = mongo.db.basecar
    query_parameters = request.args
    car_name = query_parameters.get('q')
    info_cursor = base_cars.find({"identity.name": car_name},
                                   {'_id': 0}).collation({'locale': 'en', 'strength': 2})
    info = [doc for doc in info_cursor]
    return jsonify({'info': info})


@app.route('/api/v1/resources/cars/search', methods=['GET'])
def search_car():
    car_posts = mongo.db.carpost
    query_parameters = request.args
    brand = query_parameters.get('brand', default="")
    line = query_parameters.get('line', default="")
    trim_level = query_parameters.get('trim_level', default="")
    sub_version = query_parameters.get('sub_version', default="")
    transmission = query_parameters.get('transmission', default="")
    car_status = query_parameters.get('status', default="all")
    year = query_parameters.get('year', default="all")
    engine_volume = query_parameters.get('engine_volume', default="")
    city = query_parameters.get('location', default='all')
    # source = query_parameters.get('source', default="all")
    price_min = int(float(query_parameters.get('min_price', default=0)))*1000000
    price_max = int(float(query_parameters.get('max_price', default=100000)))*1000000

    list_car_cursor = car_posts.find({"$and": [{"brand": brand},
                                               {"line": line},
                                               {"$or": [{"trim_level": trim_level}, {"trim_level": "other"}]},
                                               {"$or": [{"transmission": transmission}, {"transmission": "other"}]},
                                               {"$or": [{"engine_volume": engine_volume}, {"engine_volume": "other"}]},
                                               {"$or": [{"sub_version": sub_version}, {"sub_version": "other"}]},
                                               {"$and": [{"price": {"$lte": price_max}}, {"price": {"$gte": price_min}}]}
                                               ]},
                                     {'_id': 0}).collation({'locale': 'en', 'strength': 2}).sort("price", pymongo.ASCENDING)
    # list_car_cursor = car_posts.find({"$and": [{"brand": brand}, {"line": line}]},
    #                           {'_id': 0}).collation({'locale': 'en', 'strength': 2})
    list_car_raw = [car for car in list_car_cursor]
    list_car = []
    post_title = []
    for car in list_car_raw:
        if car['post_title'] not in post_title:
            post_title.append(car['post_title'])
            list_car.append(car)
    if year != "all" and year != "":
        list_car = [car for car in list_car if car['year'] == year]
    if car_status != "all" and car_status != "":
        list_car = [car for car in list_car if car['status'] == car_status]
    if city != "all" and city != "":
        list_car = [car for car in list_car if city in car['location']]
    for car in list_car:
        if car['source'] == "Banxehoi.com":
            car['src_img'] = 'static/img/banxehoi.jpg'
        if car['source'] == "carmudi.vn":
            car['src_img'] = 'static/img/carmudi.png'
        if car['source'] == "Chotot.com":
            car['src_img'] = 'static/img/chotot.png'
        if car['source'] == "Choxe.net":
            car['src_img'] = 'static/img/choxe.png'
        car['price_text'] = convert_price(str(car['price']))
    return jsonify({'car': list_car})


@app.route('/api/v1/resources/cars/chart', methods=['GET'])
def load_chart_data():
    car_posts = mongo.db.carpost
    base_cars = mongo.db.basecar
    query_parameters = request.args
    car_name = query_parameters.get('name')
    info_cursor = base_cars.find({"identity.name": car_name},
                                 {'_id': 0}).collation({'locale': 'en', 'strength': 2})
    info = [doc for doc in info_cursor]
    print(info[0])
    list_car_cursor = car_posts.find({"$and": [{"brand": info[0]['identity']['brand']},
                                               {"line": info[0]['identity']['line']},
                                               {"$or": [{"trim_level": info[0]['identity']['trim_level']}, {"trim_level": "other"}]},
                                               {"$or": [{"transmission": info[0]['transmission']}, {"transmission": "other"}]},
                                               {"$or": [{"engine_volume": info[0]['identity']['engine_volume']}, {"engine_volume": "other"}]},
                                               {"$or": [{"sub_version": info[0]['identity']['sub_version']}, {"sub_version": "other"}]},
                                               ]},
                                     {'_id': 0}).collation({'locale': 'en', 'strength': 2})
    chart_data = [{'x': int(float(car['year'])), 'y': car['price']/1000000} for car in list_car_cursor]
    return jsonify(chart_data)


@app.route('/api/v1/resources/lines/search', methods=['GET'])
def search_line():
    query_parameters = request.args
    brand = query_parameters.get('brand')
    if brand == '':
        return []
    else:
        for car in car_label['car']:
            if car['brand'] == brand:
                return jsonify([line['model'][0] for line in car['model']])


@app.route('/api/v1/resources/cars/search_all', methods=['GET'])
def search_all_car():
    car_posts = mongo.db.carpost
    query_parameters = request.args
    brand = query_parameters.get('brand', default="")
    line = query_parameters.get('line', default="")
    car_status = query_parameters.get('status', default="all")
    year = query_parameters.get('year', default="all")
    city = query_parameters.get('location', default='all')
    price_min = int(float(query_parameters.get('min_price', default=0)))*1000000
    price_max = int(float(query_parameters.get('max_price', default=100000)))*1000000

    if brand == '' and line != '':
        list_car_cursor = car_posts.find({"$and": [{"line": line},
                                                   {"$and": [{"price": {"$lte": price_max}},
                                                             {"price": {"$gte": price_min}}]}
                                                   ]},
                                         {'_id': 0}).collation({'locale': 'en', 'strength': 2}).sort("price",
                                                                                                     pymongo.ASCENDING)
    elif brand != '' and line == '':
        list_car_cursor = car_posts.find({"$and": [{"brand": brand},
                                                   {"$and": [{"price": {"$lte": price_max}},
                                                             {"price": {"$gte": price_min}}]}
                                                   ]},
                                         {'_id': 0}).collation({'locale': 'en', 'strength': 2}).sort("price",
                                                                                                     pymongo.ASCENDING)
    elif brand != '' and line != '':
        list_car_cursor = car_posts.find({"$and": [{"brand": brand},
                                                   {"line": line},
                                                   {"$and": [{"price": {"$lte": price_max}}, {"price": {"$gte": price_min}}]}
                                                   ]},
                                         {'_id': 0}).collation({'locale': 'en', 'strength': 2}).sort("price", pymongo.ASCENDING)
    else:
        list_car_cursor = car_posts.find({"$and": [{"$and": [{"price": {"$lte": price_max}},
                                                             {"price": {"$gte": price_min}}]}
                                                   ]},
                                         {'_id': 0}).collation({'locale': 'en', 'strength': 2}).sort("price",
                                                                                                     pymongo.ASCENDING)
    # list_car_cursor = car_posts.find({"$and": [{"brand": brand}, {"line": line}]},
    #                           {'_id': 0}).collation({'locale': 'en', 'strength': 2})
    list_car_raw = [car for car in list_car_cursor]
    list_car = []
    post_title = []
    for car in list_car_raw:
        if car['post_title'] not in post_title:
            post_title.append(car['post_title'])
            list_car.append(car)
    if year != "all" and year != "":
        list_car = [car for car in list_car if car['year'] == year]
    if car_status != "all" and car_status != "":
        list_car = [car for car in list_car if car['status'] == car_status]
    if city != "all" and city != "":
        list_car = [car for car in list_car if city in car['location']]
    for car in list_car:
        if car['source'] == "Banxehoi.com":
            car['src_img'] = 'static/img/banxehoi.jpg'
        if car['source'] == "carmudi.vn":
            car['src_img'] = 'static/img/carmudi.png'
        if car['source'] == "Chotot.com":
            car['src_img'] = 'static/img/chotot.png'
        if car['source'] == "Choxe.net":
            car['src_img'] = 'static/img/choxe.png'
        car['price_text'] = convert_price(str(car['price']))
    return jsonify({'car': list_car})


if __name__ == '__main__':
    application = DispatcherMiddleware(frontend, {
        '/api': app
    })
    base = mongo.db.basecar
    base.create_index([("identity.brand", 1),
                            ("identity.line", 1)])
    base.create_index([("identity.name", "text")])
    app.run()
