from flask import Blueprint

# from apps.models import Permission

# 创建主蓝图
main = Blueprint('main', __name__)

from . import views, errors


# @main.app_context_processor
# def inject_permissions():
#     return dict(Permission=Permission)
