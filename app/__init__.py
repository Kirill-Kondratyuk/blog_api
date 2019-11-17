from flask import Flask, jsonify, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_restful import Api

app = Flask(__name__)

cors = CORS(app, resources=r'/*', allow_credentials=True, expose_headers='*',
            allow_headers=['Content-Type', 'Authorization'],
            origins='*')
app.config.from_object(Config)
db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)
login = LoginManager(app)
jwt = JWTManager()
jwt.init_app(app)

auth = Blueprint('auth', __name__, url_prefix='/api/auth')
blog = Blueprint('blog', __name__, url_prefix='/api/blog')

auth_api = Api(auth)
blog_api = Api(blog)

from app import resources, models
from tests import actions

blog_api.add_resource(resources.PostPage, '/posts/<int:page_size>/<int:page_number>')
blog_api.add_resource(resources.Post, '/post')

auth_api.add_resource(resources.UserAccount, '/account')
auth_api.add_resource(resources.UserLogin, '/login')
auth_api.add_resource(resources.RefreshToken, '/refresh_token')
auth_api.add_resource(resources.AccessLogout, '/logout/access')
auth_api.add_resource(resources.RefreshLogout, '/logout/refresh')

app.register_blueprint(auth)
app.register_blueprint(blog)


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
    return jsonify({'message': 'The token is invalid'+invalid_token}), 401


@jwt.unauthorized_loader
def unauthorized_user_callback(callback):
    return jsonify({'message': 'Authorization failed'}), 401

