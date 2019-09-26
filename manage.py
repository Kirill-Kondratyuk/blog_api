from app import app, db
from app.models import User, Post, Comment
from tests.test_data.fills import create_posts as cp
from tests.test_data.fills import create_comments as cc
from tests.test_data.fills import create_users as cu


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'User': User,
            'Post': Post,
            'Comment': Comment,
            'cp': cp,
            'cc': cc,
            'cu': cu}