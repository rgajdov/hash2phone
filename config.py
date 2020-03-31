import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    HOST = "10.10.7.238"
    PORT = 5000
