from flask import Flask
from flasgger import Swagger
from pymongo import MongoClient

bok = """-----BEGIN RSA PUBLIC KEY-----
MEgCQQCZScdB8AFwcrZDOLVsBT7m+KyuARWixZCstV99oOMYD318o0rhAqSYk/3Q
nxV31GMYcJv7qABEqnowEkTGDh1TAgMBAAE=
-----END RSA PUBLIC KEY-----"""

bpk = """-----BEGIN RSA PRIVATE KEY-----
MIIBPQIBAAJBAJlJx0HwAXBytkM4tWwFPub4rK4BFaLFkKy1X32g4xgPfXyjSuEC
pJiT/dCfFXfUYxhwm/uoAESqejASRMYOHVMCAwEAAQJBAJTydLSkgrGCNYpSEy9Y
VYvXfOtDUIOul2rKfnQzHWRQWX8MntoQTdw30v2gQuDI8gEpBqP4llYOM8ws4BTb
sykCIwC4TePUAVtG0TME+7GE4Ont6iOkAq3WpqV7M9M062Vd/JTtAh8A1OsgEVsk
g7bwB1lLa5TT8gR1tOV0oGB31KI9G3M/AiMAjK/QaOY8MdvBcV1cDg3OJDGl0S3G
W2NMULan0+6Yq10CpQIeLhj952QRQscfrqehkZg2TwayKUkod/SK3SmHC2NnAiI+
g4WPPFxHv/30FacTi1BTf2HD32FQ3KtKdu+hi6v7JeLq
-----END RSA PRIVATE KEY-----"""

app = Flask(__name__)
swag = Swagger(app)
db = MongoClient().odc

from . import controllers
