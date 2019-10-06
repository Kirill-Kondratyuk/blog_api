from app import app, db
from app.models import UserModel, PostModel, CommentModel
from tests.test_data.fills import create_posts as cp
from tests.test_data.fills import create_comments as cc
from tests.test_data.fills import create_users as cu


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'UserModel': UserModel,
            'PostModel': PostModel,
            'CommentModel': CommentModel,
            'cp': cp,
            'cc': cc,
            'cu': cu}