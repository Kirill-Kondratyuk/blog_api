class Config(object):
    SECRET_KEY = 'YOU-WILL-NEVER-PASS'
    SQLALCHEMY_DATABASE_URI = 'postgres://admin:Kirill0201@localhost/blog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_HEADERS = 'Content-Type'
    JWT_SECRET_KEY = 'jwt-secret-string'
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
