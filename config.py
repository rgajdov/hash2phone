import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    HOST = "192.168.0.234"
    PORT = 5000
