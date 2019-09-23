from flask import jsonify, request
from app import app, db
from app.models import User, Post, Comment


@app.route('/test/comments', methods=['GET', 'DELETE'])
def _comments():
    if request.method == 'GET':
        comments = Comment.query.all()
        return jsonify({
            'comments': [
                {
                    'id': comment.id,
                    'body': comment.body[0:20],
                    'timestamp': comment.timestamp,
                    'user_id': comment.user_id,
                    'post_id': comment.post_id
                } for comment in comments
            ]
        })
    else:
        comments = Comment.query.all()
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
        return jsonify({'status': 'deleted'})


@app.route('/test/posts', methods=['GET', 'DELETE'])
def _posts():
    if request.method == 'GET':
        posts = Post.query.all()
        return jsonify({
            'posts': [
                {
                    'id': post.id,
                    'body': post.body[0:20],
                    'timestamp': post.timestamp,
                    'user_id': post.user_id
                } for post in posts
            ]
        })
    else:
        posts = Post.query.all()
        for post in posts:
            db.session.delete(post)
        db.session.commit()
        return jsonify({'status': 'deleted'})


@app.route('/test/users', methods=['GET', 'DELETE'])
def _users():
    if request.method == 'GET':
        users = User.query.all()
        return jsonify({
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'password_hash': user.password_hash
                } for user in users
            ]
        })
    else:
        users = User.query.all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'deleted'})
