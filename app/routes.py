from flask import render_template, jsonify, request, abort
from app import app
import sqlite3
from sqlite3 import Error
import re
import requests
import json

DATABASE = r"/mnt/data/DB/phone2hash/data.db"
API_URL = "https://www.megafon.ru/api/mfn/info"

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
    'Connection': 'keep-alive',
    'Host': 'www.megafon.ru',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0',
}

PHONE_NAMES = {
    '+79628894149': 'Ростислав Гайдов',
    '+79384540828': 'Ростислав Гайдов (рабочий)',
    '+79167809552': 'Илья Крестелев',
    '+79531137155': 'Илья Крестелев (2)',
    '+79037491052': 'Евгений Новиков',
    '+79104272196': 'Дамир Кирамов',
    '+79189109766': 'Николай Абашидзе',
    '+79384540826': 'Николай Абашидзе (рабочий)',
    '+79787617620': 'Михаил Медведев',
    '+79384540836': 'Михаил Медведев (рабочий)',
    '+79002916679': 'Сергей Лубин',
    '+79186560693': 'Александр Скиданов',
    '+79284474176': 'Алексей Скорых',
    '+79054028648': 'Алексей Скорых (рабочий)',
    '+79067658651': 'Рустам Юсупов',
    '+79654821780': 'Рустам Юсупов (2)',
    '+79119118666': 'Егор Пенчуков',
    '+79186019209': 'Павел Лебакин',
    '+79529783110': 'Павел Лебакин (2)',
    '+79064213088': 'Алексей Верхогляд',
    '+79184094456': 'Данила Алферов',
    '+79891684387': 'Георгий Гоцкало',
    '+79604791036': 'Кирилл Логашев',
    '+79613150288': 'Андрей Иванченко',
    '+79788397081': 'Виталий Леонидов-Каневский',
    '+79884047086': 'Александр Мармышев',
    '+79002848028': 'Александр Акулич',
}


def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)
    return conn


def validate_phone(phone_number):
    if phone_number is not None:
        pattern = '^+79\d{9}$'
        return re.search(pattern, phone_number)
    else:
        return None


def get_hash_by_phone(conn, phone):
    try:
        phone_number = "+7" + phone
        cur = conn.cursor()
        sql = "SELECT phone_hash FROM hashes WHERE phone_num = ?"
        records = cur.execute(sql, (phone_number,))
        for row in records:
            return row[0]
    except Error:
        return None


def get_phone_by_hash(conn, hash_number):
    try:
        cur = conn.cursor()
        sql = "SELECT phone_num FROM hashes WHERE phone_hash = ?"
        records = cur.execute(sql, (hash_number,))
        for row in records:
            return row[0]
    except Error:
        return None


def get_phone_info(phone_number):
    if phone_number is not None:
        phone = phone_number[1:]
        payload = {'msisdn': phone}
        data = {}
        try:
            response = requests.get(API_URL, params=payload)
            if response.status_code == 200:
                data = json.loads(response.text)
            else:
                return response.status_code
        except requests.exceptions.TooManyRedirects:
            abort(500, description="Too many redirects")
        return data
    else:
        return None


def get_owner_name(phone_num):
    if phone_num in PHONE_NAMES:
        return PHONE_NAMES[phone_num]
    else:
        return "Somebody"


@app.errorhandler(400)
def query_format_error(e):
    return jsonify(error=str(e)), 400


@app.errorhandler(404)
def resource_not_found(e):
    return jsonify(error=str(e)), 404


@app.route('/')
def index():
    user = {'username': 'dude'}
    return render_template('index.html', title='Home', user=user)


@app.route('/database/', methods=['GET', 'POST'])
def query_form():
    return render_template('query_form.html', title='Get phone info')


@app.route('/getinfo', methods=['GET', 'POST'])
def getinfo():

    data = {}
    phone_info = 0

    query_type = request.args.get('t', 0)
    query_string = request.args.get('q', 0)

    pattern_hash = '^[A-Fa-f0-9]{64}$'
    pattern_phone = '^9\d{9}$'

    conn = create_connection(DATABASE)

    if query_type == "1":
        if re.search(pattern_hash, query_string):
            phone_info = get_phone_info(get_phone_by_hash(conn, query_string))
            phone = get_phone_by_hash(conn, query_string)
            if phone is not None:
                data['phone'] = phone
                data['hash'] = query_string
                data['owner'] = get_owner_name(phone)
            else:
                abort(404, description="Unknown hash value")
        else:
            abort(400, description="SHA-256 format error")
    elif query_type == "2":
        if re.search(pattern_phone, query_string):
            phone = "+7" + query_string
            phone_info = get_phone_info(phone)
            data['phone'] = phone
            data['hash'] = get_hash_by_phone(conn, query_string)
            data['owner'] = get_owner_name(phone)
        else:
            abort(400, description="Phone number format error")
    else:
        abort(400, description="Unknown query type")

    conn.close()

    if phone_info is dict:
        return jsonify(phone=data['phone'], phone_operator=phone_info['operator'], phone_region=phone_info['region'], hash=data['hash'], owner=data['owner'])
    else:
        return jsonify(phone=data['phone'], hash=data['hash'], owner=data['owner'])
