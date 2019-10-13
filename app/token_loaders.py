from app import jwt
from flask import jsonify
from app.models import RevokedToken


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return RevokedToken.is_jti_blacklisted(jti)


@jwt.expired_token_loader
def expired_token_callback(expired_token):
    token_type = expired_token['type']
    return jsonify({
        'status': 401,
        'sub_status': 42,
        'msg': 'The {} token has expired'.format(token_type)
    }), 401


@jwt.invalid_token_loader
def invalid_token_callback(invalid_token):
    return jsonify({'message': 'The token is invalid'+invalid_token}), 401


@jwt.unauthorized_loader
def unauthorized_user_callback(callback):
    return jsonify({'message': 'Authorization failed'}), 401