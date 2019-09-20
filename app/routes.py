from flask import jsonify, request
from validate_email import validate_email
from flask import Response
from app import app
from app import db
from app.models import User, Post


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


@app.route('/api/registration/email_existense', methods=['POST'])
def check_email_exists():
    if request.method == 'POST':
        body = request.get_json()
        email_value = body.get('value')
        is_valid = validate_email(email_value, check_mx=True)
        if not is_valid:
            is_valid = False
        return jsonify({'exists': is_valid})
