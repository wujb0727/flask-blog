from flask import jsonify

# 用户没有权限访问
from wtforms import ValidationError

from apps.api import api


def forbidden(message):
    response = jsonify({'error': 'Forbidden', 'message': message})
    response.status_code = 403
    return response


# 用户身份未认证
def unauthorized(message):
    response = jsonify({'error': 'Unauthorized', message: message})
    response.status_code = 401
    return response


# 请求无效或不一致
def bad_request(message):
    response = jsonify({'error': 'Bad Request', message: message})
    response.status_code = 400
    return response


@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
