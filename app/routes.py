from flask import jsonify, request
from marshmallow import ValidationError
from validate_email import validate_email
from app import app
from app import db
from app.models import User, UserSchema, Post


@app.route('/api/<int:page>')
def blog(page):
    posts = Post.query.paginate(per_page=10, page=int(page))
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


@app.route('/api/registration/account', methods=['POST'])
def account():
    if request.method == 'POST':
        data = request.get_json()
        try:
            UserSchema().load(data)
        except ValidationError as vall_err:
            print(vall_err)
            return 'Invalid input data'
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
