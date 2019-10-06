from flask import jsonify, request
from app import app, db
from app.models import UserModel, PostModel, CommentModel
from .test_data.fills import create_users, create_comments, create_posts


@app.route('/test/comments', methods=['GET', 'DELETE', 'POST'])
def _comments():
    if request.method == 'GET':
        comments = CommentModel.query.all()
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
    elif request.method == 'DELETE':
        comments = CommentModel.query.all()
        for comment in comments:
            db.session.delete(comment)
        db.session.commit()
        return jsonify({'status': 'deleted'})
    else:
        comments = create_comments(2)
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


@app.route('/test/posts', methods=['GET', 'DELETE', 'POST'])
def _posts():
    if request.method == 'GET':
        posts = PostModel.query.all()
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
    elif request.method == 'DELETE':
        posts = PostModel.query.all()
        for post in posts:
            db.session.delete(post)
        db.session.commit()
        return jsonify({'status': 'deleted'})
    else:
        posts = create_posts(2)
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


@app.route('/test/users', methods=['GET', 'DELETE', 'POST'])
def _users():
    if request.method == 'GET':
        users = UserModel.query.all()
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
    elif request.method == 'DELETE':
        users = UserModel.query.all()
        for user in users:
            db.session.delete(user)
        db.session.commit()
        return jsonify({'status': 'deleted'})
    else:
        users = create_users(10)
        return jsonify({
            'users': [{
                'id': user.id,
                'username': user.username,
                'email': user.email
            } for user in users]
        })
