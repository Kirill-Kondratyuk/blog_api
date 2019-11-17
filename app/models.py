from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from marshmallow import Schema, fields
from marshmallow.validate import Length


class UserModel(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(60), unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('PostModel', backref='author', lazy='dynamic')
    comments = db.relationship('CommentModel', backref='user', lazy='dynamic')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        posts = self.posts.all()
        for post in posts:
            comments = post.comments.all()
            for comment in comments:
                db.session.delete(comment)
            db.session.delete(post)
        comments = self.comments.all()
        for comment in comments:
            db.session.delete(comment)
        db.session.delete(self)
        db.session.commit()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def __repr__(self):
        return f'<User: {self.username}. Email: {self.email}. Id: {self.id}>'


@login.user_loader
def load_user(user_id):
    return UserModel.query.get(int(user_id))


class PostModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))
    comments = db.relationship('CommentModel', backref='post', lazy='dynamic')

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        comments = self.comments.all()
        for comment in comments:
            db.session.delete(comment)
            db.session.commit()
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<PostModel: {self.body}. Date: {self.timestamp}>'


class CommentModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user_model.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post_model.id'))

    def __repr__(self):
        return f'CommentModel: {self.body}'


UserSchema = Schema.from_dict(
    {
        'username': fields.Str(required=True, validate=Length(min=3, max=60)),
        'password': fields.Str(required=True, validate=Length(min=8, max=128)),
        'email': fields.Str(required=True, validate=Length(max=60)),
    }
)
PostSchema = Schema.from_dict(
    {
        'title': fields.Str(required=True, validate=Length(min=3, max=40)),
        'body': fields.Str(required=True)
    }
)


class RevokedToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120))

    def add(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti):
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)
