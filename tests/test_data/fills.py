import string
import random


from app import db
from app.models import UserModel, PostModel, CommentModel


def rand_str(length: int):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(0, length, 1))


def create_users(amount: int):
    users = [UserModel(username=rand_str(20), email=rand_str(8)) for i in range(0, amount, 1)]
    for user in users:
        db.session.add(user)
        db.session.commit()
    return users


def create_posts(amount: int):
    users = UserModel.query.all()
    posts = []
    for i in range(0, amount, 1):
        for user in users:
            body = ''
            for j in range(0, 10, 1):
                body += rand_str(5)+' '
            post = PostModel(body=body, user_id=user.id)
            db.session.add(post)
            db.session.commit()
            posts.append(post)
    return posts


def create_comments(amount):
    users = UserModel.query.all()
    posts = PostModel.query.all()
    comments = []
    for i in range(0, amount, 1):
        body = ''
        for j in range(0, 3, 1):
            body += rand_str(10) + ' '
        comment = CommentModel(body=body, user_id=random.choice(users).id, post_id=random.choice(posts).id)
        db.session.add(comment)
        db.session.commit()
        comments.append(comment)
    return comments

