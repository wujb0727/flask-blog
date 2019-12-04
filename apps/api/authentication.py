from flask import g, jsonify, request
from flask_httpauth import HTTPBasicAuth

from apps.api import api
from apps.api.errors import unauthorized, forbidden
from apps.models import User

auth = HTTPBasicAuth()


# 验证请求（根据请求中所带的认证信息）是否为认证请求，如果是认证请求返回True，并且把请求中
# 的用户实例放到g.current_user里面，如果请求不是认证请求，返回False
@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('用户身份未认证')


@api.before_request
@auth.login_required
def before_request():
    if not g.current_user.is_anonymous and not g.current_user.confirmed:
        return forbidden('未认证或激活的账号')


@api.route('/tokens/', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('无效的用户')
    return jsonify({
        'token': g.current_user.generate_auth_token(expiration=7*24*3600),
        'expiration': 7*24*3600,
    })
