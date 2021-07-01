import os
import sys

from flasgger import Swagger
from flask import Flask
from pymongo import MongoClient

bok_location = os.getenv("bok_location")
bpk_location = os.getenv("bpk_location")
if bok_location is None or bpk_location is None:
    print("bpk/bok location not provided", file=sys.stderr)
    sys.exit()

try:
    bok_file = open(bok_location, "r")
    bok = bok_file.read()

    bpk_file = open(bpk_location, "r")
    bpk = bpk_file.read()
except:
    print("Failed to read bpk/bok from file", file=sys.stderr)
    sys.exit()

mongo_uri = os.getenv("mongo_uri")
if mongo_uri is None:
    mongo_uri = "mongodb://127.0.0.1:27017"

app = Flask(__name__)
swag = Swagger(app)
db = MongoClient(mongo_uri).odc

from . import controllers
