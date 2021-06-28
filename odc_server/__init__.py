from flask import Flask
from flasgger import Swagger
from pymongo import MongoClient

app = Flask(__name__)
swag = Swagger(app)
db = MongoClient().odc

from . import controllers
