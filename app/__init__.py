from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_restful import Api

app = Flask(__name__)
api = Api(app)
CORS(app, resources=r"/*", allow_credentials=True, expose_headers="*", allow_headers='Content-Type', origins="*")
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)

migrate = Migrate(app, db)
login = LoginManager(app)


from app import controllers, models, errors
from tests import actions
