from flask import jsonify, request, make_response, Blueprint
from flask_restful import Resource
from marshmallow import ValidationError
from validate_email import validate_email
from app.models import UserModel, UserSchema, PostModel, RevokedToken
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)
from app import app

auth = Blueprint('auth', __name__, url_prefix='/api/auth')
blog = Blueprint('blog', __name__, url_prefix='/api/blog')


@blog.route('/posts/<int:page_size>/<int:page_number>', methods=['GET'])
def post_page(page_size, page_number):
    posts = PostModel.query.paginate(per_page=int(page_size), page=int(page_number))
    response = {
        'posts': [
            {
                'body': post.body,
                'username': post.author.username,
                'timestamp': post.timestamp
            } for post in posts.items
        ],
        'pages': posts.pages
    }
    return jsonify(response)


@auth.route('/account', methods=['POST', 'GET', 'PUT', 'DELETE'])
def user_account():
    if request.method == 'POST':
        message = {
            'errors': {}
        }
        data = request.get_json()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        username_valid = False if UserModel.find_by_username(username) else True
        email_valid = False if UserModel.find_by_email(email) else True
        email_exists = True if validate_email(email, check_mx=True) else False
        if not username_valid:
            message['errors']['UsernameExistsError'] = 'UserModel with such username already exists'
        if not email_valid:
            message['errors']['UserWithSuchEmailExists'] = 'UserModel with such email already exists'
        if not email_exists:
            message['errors']['EmailDoesNotExistError'] = 'Entered email does not exist'
        try:
            UserSchema().load(data)
        except ValidationError as vall_err:
            message['errors']['ValidationError'] = vall_err.messages
            return make_response(jsonify(message), 400)
        else:
            if message['errors']:
                return make_response(jsonify(message), 400)
            user = UserModel(username=username, email=email)
            user.set_password(password)
            user.save_to_db()
            return make_response(jsonify(message), 201)


@auth.route('/login', methods=['POST', 'GET'])
def user_login():
    if request.method == 'GET':
        current_user = get_jwt_identity()
        return make_response({'username': current_user}, 200)
    elif request.method == 'POST':
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = UserModel.find_by_email(email)
        if not user:
            return make_response({'message': 'invalid data has been entered'}, 400)
        if user.check_password(password):
            return make_response({'username': user.username,
                                  'access_token': create_access_token(identity=user.username),
                                  'refresh_token': create_refresh_token(identity=user.username)})
        else:
            return make_response({'message': 'invalid data has been entered'}, 400)


@auth.route('/refresh_token', methods=['POST'])
@jwt_refresh_token_required
def token_refresh():
    if request.method == 'POST':
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return make_response({'access_token': access_token})


@auth.route('/logout/access', methods=['POST'])
@jwt_required
def user_logout_access():
    if request.method == 'POST':
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Access toke has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


@auth.route('/logout/refresh', methods=['POST'])
@jwt_refresh_token_required
def user_logout_refresh():
    if request.method == 'POST':
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
