# coding: utf-8
from flask import Flask
# from flask_cors import CORS


app = Flask(__name__)

# CORS(app, resources=r'/*')  # 添加的

from App.controller import indexController

