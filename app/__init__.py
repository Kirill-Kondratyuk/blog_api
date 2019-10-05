from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_restful import Api
from flask_jwt_extended import JWTManager

app = Flask(__name__)
api = Api(app, catch_all_404s=True)
CORS(app, resources=r"/*", allow_credentials=True, expose_headers="*", allow_headers='Content-Type', origins="*")
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
login = LoginManager(app)
jwt = JWTManager(app)


from app import resources, models
from tests import actions

api.add_resource(resources.UserRegistration, '/api/auth/account')
api.add_resource(resources.Posts, '/api/posts/<int:page_size>/<int:page_number>')
api.add_resource(resources.SecretInfo, '/api/secret_info')
api.add_resource(resources.UserLogin, '/api/auth/login')


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)
