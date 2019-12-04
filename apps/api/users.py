from flask import jsonify

from apps.api import api
from apps.models import User


# 返回所有用户
@api.route('/users/')
def get_users():
    users = User.query.all()
    return jsonify({'users': [user.to_json() for user in users]})


# 返回一个用户
@api.route('/users/<int:id>/')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


# 返回一个用户发布的所有博客文章
@api.route('/users/<int:id>/posts/')
def get_posts_for_user(id):
    posts = User.query.get_or_404(id).posts
    return jsonify({'posts': [post.to_json() for post in posts]})


# 返回一个用户所关注用户发布的所有文章
@api.route('/users/<int:id>/timeline/')
def get_posts_for_followed(id):
    posts = User.query.get_or_404(id).followed_posts.all()
    return jsonify({'posts': [post.to_json() for post in posts]})


# 返回一个用户关注的所有博主
@api.route('/users/<int:id>/followed/')
def get_followed_for_user(id):
    follows = User.query.get_or_404(id).is_fans
    return jsonify({'is_fans': [follow.to_json() for follow in follows]})


# 返回一个用户的所有粉丝
@api.route('/users/<int:id>/follower/')
def get_follower_for_user(id):
    follows = User.query.get_or_404(id).is_blogger
    return jsonify({'is_blogger': [follow.to_json() for follow in follows]})
