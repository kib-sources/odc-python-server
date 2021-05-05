from flask import Flask
from flasgger import Swagger

app = Flask(__name__)
swag = Swagger(app)

from . import controllers
