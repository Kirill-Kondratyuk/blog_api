from flask import jsonify, request, make_response
from flask_restful import Resource, reqparse
from marshmallow import ValidationError
from validate_email import validate_email
from app import db
from app.models import UserModel, UserSchema, PostModel, RevokedToken
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)


class Posts(Resource):
    def get(self, page_size, page_number):
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


class UserRegistration(Resource):
    def post(self):
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


class UserLogin(Resource):
    def get(self):
        current_user = get_jwt_identity()
        return {'username': current_user}, 200

    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        user = UserModel.find_by_email(email)
        if not user:
            return {'message': 'invalid data has been entered'}, 400
        if user.check_password(password):
            return {'access_token': create_access_token(identity=user.username),
                    'refresh_token': create_refresh_token(identity=user.username)}


class SecretInfo(Resource):
    @jwt_required
    def get(self):
        current_user = get_jwt_identity()
        return {'Logged in as ': current_user}


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
