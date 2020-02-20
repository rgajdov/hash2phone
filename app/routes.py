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
            data = json.loads(response.text)
        except requests.exceptions.TooManyRedirects:
            abort(500, description="Too many redirects")
        return data
    else:
        return None


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

    query_type = request.args.get('t', 0)
    query_string = request.args.get('q', 0)

    pattern_hash = '^[A-Fa-f0-9]{64}$'
    pattern_phone = '^9\d{9}$'

    conn = create_connection(DATABASE)

    if query_type == "1":
        if re.search(pattern_hash, query_string):
            data = get_phone_info(get_phone_by_hash(conn, query_string))
            if data is not None:
                data['phone'] = get_phone_by_hash(conn, query_string)
                data['hash'] = query_string
            else:
                abort(404, description="Unknown hash value")
        else:
            abort(400, description="SHA-256 format error")
    elif query_type == "2":
        if re.search(pattern_phone, query_string):
            phone = "+7" + query_string
            data = get_phone_info(phone)
            if data is not None:
                data['phone'] = phone
                data['hash'] = get_hash_by_phone(conn, query_string)
            else:
                abort(404, description="Unknown phone number")
        else:
            abort(400, description="Phone number format error")
    else:
        abort(400, description="Unknown query type")

    conn.close()

    return jsonify(phone=data['phone'], phone_operator=data['operator'], phone_region=data['region'], hash=data['hash'])
