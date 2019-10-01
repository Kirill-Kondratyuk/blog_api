from flask import jsonify, request, make_response
from flask_restful import Resource, reqparse
from marshmallow import ValidationError
from validate_email import validate_email
from app import db
from app.models import User, UserSchema, Post, RevokedToken
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

registration_parser = reqparse.RequestParser()
registration_parser.add_argument('username', help='This field cannot be blank', required=True)
registration_parser.add_argument('email', help='This field cannot be blank', required=True)
registration_parser.add_argument('password', help='This field cannot be blank', required=True)


class Posts(Resource):
    def get(self, page_size, page_number):
        posts = Post.query.paginate(per_page=int(page_size), page=int(page_number))
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


class UserRegistration(Resource):
    def post(self):
        message = {
            'errors': {}
        }
        data = registration_parser.parse_args()
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        username_valid = False if User.find_by_username(username) else True
        email_valid = False if User.find_by_email(email) else True
        email_exists = True if validate_email(email, check_mx=True) else False
        if not username_valid:
            message['errors']['UsernameExistsError'] = 'User with such username already exists'
        if not email_valid:
            message['errors']['UserWithSuchEmailExists'] = 'User with such email already exists'
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
            user = User(username=username, email=email)
            user.set_password(password)
            user.save_to_db()
            message['access_token'] = create_access_token(identity=username)
            message['refresh_token'] = create_refresh_token(identity=username)
            return make_response(jsonify(message), 201)


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class UserLogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Access toke has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500


class UserLogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = RevokedToken(jti=jti)
            revoked_token.add()
            return {'message': 'Refresh token has been revoked'}
        except:
            return {'message': 'Something went wrong'}, 500
