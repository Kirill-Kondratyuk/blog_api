from flask import Flask, jsonify
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
CORS(app, resources=r"/*", allow_credentials=True, expose_headers="*",
     allow_headers=['Content-Type', 'Authorization'],
     origins="*")
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
api.add_resource(resources.UserLogoutAccess, '/api/auth/logout/access')
api.add_resource(resources.UserLogoutRefresh, '/api/auth/logout/refresh')


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return models.RevokedToken.is_jti_blacklisted(jti)


@jwt.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(invalid_token):
    token_type = invalid_token['type']
    return jsonify({'message': 'The {} token is invalid'.format(token_type)}), 401


@jwt.unauthorized_loader
def unauthorized_user_callback():
    return jsonify({'message': 'Authorization failed'}), 401
