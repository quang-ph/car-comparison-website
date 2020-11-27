from urllib.parse import urljoin
import datetime

transmissions = ['AT', 'MT', 'CVT']
truck_brands = ['Thaco', 'Isuzu', 'Hino', 'JAC', 'jac' 'Hiro', 'Ben', 'Fuso', 'Dongfeng', 'Deahan',
                'Deahan Tera', 'Towner', 'Veam', 'Kenbo']


def format_base_identity(df, car_label, value):
    identity = {'name': value,
                'engine_volume': 'other',
                'sub_version': 'other',
                'trim_level': 'other'}

    for index, row in df.iterrows():
        if row['line'].lower() in value.lower():
            identity['line'] = row['line']
            identity['brand'] = row['brand']
            break
        else:
            identity['line'] = ''
            identity['brand'] = ''

    if identity['brand'].lower() not in value.lower():
        identity['name'] = identity['brand'] + " " + value

    for label in car_label['car']:
        if label['brand'].lower() in identity['brand'].lower():
            for line in label['model']:
                for model in line['model']:
                    if model.lower() in identity['line'].lower():
                        identity['line'] = line['model'][0]
                        if len(line['engine_volume']) == 1:
                            identity['engine_volume'] = line['engine_volume'][0]
                        else:
                            for engine in line['engine_volume']:
                                if engine.lower() in identity['name'].lower():
                                    identity['engine_volume'] = engine
                                    break
                        text = identity['name'].lower().replace(identity['brand'].lower(), "").replace(
                            identity['line'].lower(), "")
                        for sub in line['sub_version']:
                            if sub.lower() in text:
                                identity['sub_version'] = sub
                                text.replace(sub, "").replace(sub.lower(), "")
                                break
                        for trim in line['trim_level']:
                            if trim.lower() in text:
                                identity['trim_level'] = trim
                                break
                        break
    return identity


def format_base_price(value):
    value = int(float(value.replace(".", "").strip()))
    return value


def format_base_string(value):
    if value != '' and value != 'Null':
        return int(float(value))


def format_base_dimension(value):
    dict = {}
    if value != '' and value != 'Null':
        dimensions = value.split('x')
        if len(dimensions) == 3:
            dict['length'] = int(float(dimensions[0].replace(",", "")))
            dict['width'] = int(float(dimensions[1].replace(",", "")))
            dict['height'] = int(float(dimensions[2].replace(",", "")))
    return dict


def format_base_transmission(value):
    for gear in transmissions:
        if gear.lower() in value.lower():
            return gear


# Định dạng lại giá
def format_car_price(price_txt):
    if (('tỉ' in price_txt.lower()) or ('tỷ' in price_txt.lower())) and (
            ('triệu' in price_txt.lower()) or ('tr' in price_txt.lower())):
        price_str = price_txt.replace(" triệu", "").replace(" tr", "").replace(" tỉ ", ".").replace(" tỷ ", ".").strip()
        sep_index = price_str.find('.')
        if len(price_str[sep_index + 1:]) == 2:
            price_str = price_str[:sep_index + 1] + '0' + price_str[sep_index + 1:]
        fm_price = int(float(price_str) * 1000000000)
        return fm_price
    elif 'tỷ' in price_txt.lower() or 'tỉ' in price_txt.lower():
        price_str = price_txt.replace("tỷ", "").replace("tỉ", "").strip()
        fm_price = int(float(price_str) * 1000000000)
        return fm_price
    elif 'triệu' in price_txt.lower():
        fm_price = int(float(price_txt.replace(" triệu", "")) * 1000000)
        return fm_price


# Định dạng lại các trường khác
def format_data(car, root_url):
    if 'tự động' in car['transmission']:
        car['transmission'] = "AT"
    elif 'sàn' in car['transmission'].lower():
        car['transmission'] = "MT"
    else:
        car['transmission'] = car.get("transmission_2")
    car['status'] = car['status'].strip(": ")
    car['year'] = car['year'].strip(": ")
    car['car_type'] = car['car_type'].strip(": ")
    if 'HCM' in car['location']:
        car['location'] = "Hồ Chí Minh"
    if 'Huế' in car['location']:
        car['location'] = "Thừa Thiên Huế"
    for img in car['images']:
        img_index = car['images'].index(img)
        if img.startswith('/') or img.startswith(root_url):
            car['images'][img_index] = urljoin(root_url, img)
    if "đã".lower() in car['status'].lower():
        car['status'] = "Cũ"
    return car


# Gán nhãn brand, line, trim_level
def set_label(car, car_label):
    ori_title = car['post_title'].lower()
    ori_version = car['version'].lower()
    ori_classify = car['classify'].lower()
    ori_brand = car['brand']
    car['line'] = "Xe khác"

    car['engine_volume'] = "other"
    car['style'] = "other"
    car['transmission_2'] = "other"
    car['sub_version'] = "other"
    car['trim_level'] = "other"

    for label in car_label['car']:
        lb_brand = label['brand']
        if (lb_brand.lower() in ori_brand) or (lb_brand.lower() in ori_classify) or (
                lb_brand.lower() in ori_title):
            car['brand'] = lb_brand
            lb_models = label['model']
            for lb_model in lb_models:
                lb_lines = lb_model['model']
                for lb_line in lb_lines:
                    if (lb_line.lower() in ori_version) or (lb_line.lower() in ori_classify) or (
                            lb_line.lower() in ori_title):
                        car['line'] = lb_model['model'][0]

                        engines = lb_model['engine_volume']
                        styles = lb_model['style']
                        transmissions = lb_model['transmission']
                        sub_versions = lb_model['sub_version']
                        trim_levels = lb_model['trim_level']

                        if len(engines) == 1:
                            car['engine_volume'] = engines[0]
                        elif len(engines) > 1:
                            for engine in engines:
                                if (engine in ori_version) or (engine in ori_classify) or (
                                        engine in ori_title):
                                    car['engine_volume'] = engine
                                    ori_version.replace(engine, "")
                                    break

                        if len(styles) == 1:
                            car['style'] = styles[0]
                        elif len(styles) > 1:
                            for style in styles:
                                if (style.lower() in ori_version) or (style.lower() in ori_classify) or (
                                        style.lower() in ori_title):
                                    car['style'] = style
                                    ori_version.replace(style.lower(), "")
                                    break

                        if len(transmissions) == 1:
                            car['transmission_2'] = transmissions[0]
                        elif len(transmissions) > 1:
                            for transmission in transmissions:
                                if (transmission.lower() in ori_version) or (transmission.lower() in ori_classify) or (
                                        transmission.lower() in ori_title):
                                    car['transmission_2'] = transmission
                                    ori_version.replace(transmission.lower(), "")
                                    break

                        for sub_version in sub_versions:
                            if (sub_version.lower() in ori_version) or (sub_version.lower() in ori_classify) or (
                                    sub_version.lower() in ori_title):
                                car['sub_version'] = sub_version
                                ori_version.replace(sub_version.lower(), "")
                                break

                        for trim_level in trim_levels:
                            if trim_level.lower() in ori_version:
                                car['trim_level'] = trim_level
                                break
                        break

                if car['line'] != "Xe khác":
                    break
            break
        else:
            for truck_brand in truck_brands:
                if (truck_brand.lower() in ori_brand) or (truck_brand.lower() in ori_classify) or (
                        truck_brand.lower() in ori_title):
                    return

    if car['brand'] != "Hãng khác" and car['line'] == "Xe khác":
        return
    else:
        return car


def format_time(time_text):
    time_text = time_text.replace("Đăng", "").strip()
    now = datetime.datetime.now()
    if "Hôm qua" in time_text:
        edit_time = now - datetime.timedelta(days=1)
        fn_time = edit_time.strftime('%Y/%m/%d')
        return fn_time
    elif "trước" in time_text:
        if "tiếng trước" in time_text:
            hour = int(float(time_text.replace("tiếng trước", "").strip()))
            edit_time = now - datetime.timedelta(hours=hour)
            fn_time = edit_time.strftime('%Y/%m/%d')
            return fn_time
        elif "tháng trước" in time_text:
            edit_time = now - datetime.timedelta(days=30)
            fn_time = edit_time.strftime('%Y/%m/%d')
            return fn_time
        elif "tuần trước" in time_text:
            week = int(float(time_text.replace("tuần trước", "").strip()))
            edit_time = now - datetime.timedelta(weeks=week)
            fn_time = edit_time.strftime('%Y/%m/%d')
            return fn_time
        elif "ngày trước" in time_text:
            days = int(float(time_text.replace("ngày trước", "").strip()))
            edit_time = now - datetime.timedelta(days=days)
            fn_time = edit_time.strftime('%Y/%m/%d')
            return fn_time
    else:
        time_text = time_text.replace("(", "").replace(")", "")
        post_time = time_text.split("/")
        fn_time = post_time[2] + "/" + post_time[1] + "/" + post_time[0]
        fn_time = datetime.datetime.strptime(fn_time, '%Y/%m/%d')
        fn_time = fn_time.strftime('%Y/%m/%d')
        return fn_time


def set_brand(dataframe, car):
    for index, row in dataframe.iterrows():
        if row['line'].lower() in car['post_title'].lower() or row['line'].lower() in car['line'].lower() \
                or row['line'].lower() in car['version'].lower() or row['line'].lower() in car['classify'].lower():
            car['line'] = row['line']
            car['brand'] = row['brand']
            break
    return car
