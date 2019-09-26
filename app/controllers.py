from flask import jsonify, request
from flask_restful import Resource
from marshmallow import ValidationError
from validate_email import validate_email
from app import db, api
from app.models import User, UserSchema, Post
import app.errors as errors


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


api.add_resource(Posts, '/api/posts/<int:page_size>/<int:page_number>')


class Registration(Resource):
    def post(self):
        data = request.get_json()
        try:
            UserSchema().load(data)
        except ValidationError as vall_err:
            payload = {'invalid': vall_err.messages}
            raise errors.BadRequest('Bad request', 400, payload)
        else:
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')

            username_valid = False if User.query.filter_by(username=username).first() else True
            email_valid = False if User.query.filter_by(email=email).first() else True
            email_exists = True if validate_email(email, check_mx=True) else False

            if email_valid and username_valid:
                user = User(username=username, email=email)
                user.set_password(password)
                db.session.add(user)
                db.session.commit()

            return jsonify({
                'email': {
                    'exists': email_exists,
                    'allowed': email_valid
                },
                'username': {
                    'allowed': username_valid
                },
                'password': {
                    'allowed': True
                }
            })


api.add_resource(Registration, '/api/registration/account')
