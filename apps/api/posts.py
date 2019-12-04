from flask import jsonify, request, g, url_for, current_app
from wtforms import ValidationError

from apps import db
from apps.api import api
from apps.api.decorators import permission_required
from apps.api.errors import forbidden
from apps.models import Post, Permission, Comment


# 返回所有博客文章
@api.route('/posts/')
def get_posts():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.paginate(page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_posts', page=pagination.prev_num)
    next = None
    if pagination.has_next:
        next = url_for('api.get_posts', page=pagination.next_num)
    return jsonify({'posts': [post.to_json() for post in posts], 'prev_url': prev, 'next_url': next})


# 返回一篇博客文章
@api.route('/posts/<int:id>/')
def get_post(id):
    post = Post.query.get_or_404(id)
    return jsonify(post.to_json())


# 创建一篇博客文章
@api.route('/posts/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_post():
    post = Post.form_json(request.json)
    post.author = g.current_user
    try:
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ValidationError('新增失败,请重试')
    return jsonify(post.to_json(), 201, {'Location': url_for('api.get_post', id=post.id)})


# 修改一篇博客文章
@api.route('/posts/<int:id>/', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and not g.current_user.can(Permission.ADMIN):
        return forbidden('没有足够的权限')
    post.body = request.json.get('body', post.body)
    try:
        db.session.add(post)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ValidationError('修改失败,请重试')
    return jsonify(post.to_json())


# 返回一篇博客文章的评论
@api.route('/posts/<int:id>/comments/')
def get_comments_for_posts(id):
    comments = Post.query.get_or_404(id).comments
    return jsonify({'comments': [comment.to_json() for comment in comments]})


# 在一篇博客文章中添加一条评论
@api.route('/posts/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.WRITE)
def new_comments_for_posts(id=id):
    comment = Comment.form_json(request.json)
    comment.user = g.current_user
    comment.post = Post.query.get_or_404(id)
    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise ValidationError('评论失败,请重试')
    return jsonify(comment.to_json(), 201, {'Location': url_for('api.get_comments', id=comment.id)})


# 返回所有评论
@api.route('/comments/')
def get_comments_list():
    comments = Comment.query.all()
    comments_json = {
        'comments': [comment.to_json() for comment in comments]
    }
    return jsonify(comments_json)


# 返回一条评论
@api.route('/comments/<int:id>/')
def get_comments(id):
    comment = Comment.query.get_or_404(id)
    return jsonify(comment.to_json())
