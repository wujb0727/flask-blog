import os
import uuid

from flask import send_from_directory, current_app, render_template, flash, redirect, url_for, request, make_response
from flask_login import login_required, current_user

from apps import db
from apps.decorators import admin_required, permission_required
from apps.main import main
from apps.main.forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from apps.models import User, Post, Follow, Comment, Permission


def random_filename(filename):
    """
    生成随机字符串组成的文件名
    :param filename: 原文件名
    :return: 随机字符串组成的文件名
    """
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


# 首页
@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get('page', 1, type=int)
    if request.cookies.get('show_followed') == 'show_followed' and current_user.is_authenticated:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(Post.created.desc()).paginate(page, per_page=10)
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.body.data, author_id=current_user.id)
        post.set_updated()
        try:
            db.session.add(post)
            db.session.commit()
        except:
            db.session.rollback()
            flash('发表失败请重试')
        return redirect(url_for('main.index'))
    context = {
        'pagination': pagination,
        'form': form,
    }
    return render_template('main/index.html', **context)


@main.route('/all/')
@login_required
def show_all():
    next = request.args.get('next')
    resp = make_response(redirect(next))
    resp.set_cookie('show_followed', 'show_all', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/show_followed/')
@login_required
def show_followed():
    next = request.args.get('next')
    resp = make_response(redirect(next))
    resp.set_cookie('show_followed', 'show_followed', max_age=30 * 24 * 60 * 60)
    return resp


# 获取服务器文件
@main.route('/uploads/<path:filename>/')
def get_file(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER']), filename)


# 用户详情
@main.route('/user/<int:id>/')
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    page = request.args.get('page', 1, type=int)
    if request.cookies.get('show_followed') == 'show_followed' and current_user.is_authenticated:
        query = user.followed_posts
    else:
        query = Post.query.filter_by(author=user)
    pagination = query.order_by(Post.created.desc()).paginate(page,
                                                              per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
                                                              error_out=False)
    context = {
        'user': user,
        'pagination': pagination,
    }
    return render_template('main/user.html', **context)


# 编辑用户资料
@main.route('/edit-profile/', methods=['GET', 'POST'])
@login_required
def edit_profile():
    user = current_user._get_current_object()
    form = EditProfileForm(obj=user)
    if form.validate_on_submit():
        user.nickname = form.nickname.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        file = form.avatar.data
        if file:
            filename = random_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], current_app.config['AVATAR_FOLDER'], filename))
            user.avatar_url = current_app.config['AVATAR_FOLDER'] + '/' + filename
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('修改失败,请重试')
            return redirect(url_for('main.edit_profile'))
        return redirect(url_for('main.user', id=user.id))
    return render_template('main/edit-profile.html', form=form)


# 管理员编辑用户资料
@main.route('/edit-profile/<int:user_id>/', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(user_id):
    user = User.query.filter_by(id=user_id).first()
    form = EditProfileAdminForm(obj=user)
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.confirmed = form.confirmed.data
        user.role_id = form.role_id.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        file = form.avatar.data
        if file:
            filename = random_filename(file.filename)
            file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], current_app.config['AVATAR_FOLDER'], filename))
            user.avatar_url = current_app.config['AVATAR_FOLDER'] + '/' + filename
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('修改失败,请重试')
            return redirect(url_for('main.edit_profile', user_id=user.id))
        return redirect(url_for('main.user', id=user.id))
    return render_template('main/edit-profile-admin.html', form=form)


# 编辑博文
@main.route('/edit-post/<int:id>/', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.filter_by(id=id).first()
    form = PostForm(obj=post)
    if form.validate_on_submit():
        post.body = form.body.data
        post.author_id = current_user.id
        post.set_updated()
        try:
            db.session.add(post)
            db.session.commit()
            next = request.args.get('next')
            return redirect(next)
        except:
            db.session.rollback()
            flash('发表失败请重试')
            return redirect(url_for('main.edit_post', id=post.id))
    return render_template('main/edit_post.html', form=form)


# 博文详情(评论)
@main.route('/post-detail/<int:id>/', methods=['GET', 'POST'])
def post_detail(id):
    user = current_user._get_current_object()
    pagination = Post.query.filter_by(id=id).paginate(page=1, per_page=10)
    post = Post.query.filter_by(id=id).first()
    comment_list = Comment.query.filter_by(post=post).order_by(Comment.timestamp.desc()).all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data, user=user, post=post)
        try:
            db.session.add(comment)
            db.session.commit()
        except:
            db.session.rollback()
            flash('评论失败,请重试')
            return redirect(url_for('main.post_detail', id=post.id))
        flash('评论成功')
        return redirect(url_for('main.post_detail', id=post.id))
    context = {
        'pagination': pagination,
        'form': form,
        'comment_list': comment_list,
    }
    return render_template('main/post-detail.html', **context)


# 关注用户
@main.route('/follow/<int:id>/')
@login_required
def follow(id):
    fans = current_user._get_current_object()
    blogger = User.query.filter_by(id=id).first()
    fans.follow(blogger)
    flash('您已成功关注{}'.format(blogger.username))
    return redirect(url_for('main.user', id=blogger.id))


# 取消关注
@main.route('/unfollow/<int:id>/')
@login_required
def unfollow(id):
    fans = current_user._get_current_object()
    blogger = User.query.filter_by(id=id).first()
    fans.unfollow(blogger)
    flash('您已取消关注{}'.format(blogger.username))
    return redirect(url_for('main.user', id=blogger.id))


# 粉丝列表
@main.route('/fans-list/<int:id>/')
def fans_list(id):
    user = User.query.filter_by(id=id).first()
    page = request.args.get('page', 1, type=int)
    pagination = user.is_blogger.order_by(Follow.timestamp.desc()).paginate(page, per_page=10)
    context = {
        'user': user,
        'pagination': pagination
    }
    return render_template('main/fans-list.html', **context)


# 关注列表
@main.route('/follow-list/<int:id>/')
def follow_list(id):
    user = User.query.filter_by(id=id).first()
    page = request.args.get('page', 1, type=int)
    pagination = user.is_fans.order_by(Follow.timestamp.desc()).paginate(page, per_page=10)
    context = {
        'user': user,
        'pagination': pagination
    }
    return render_template('main/follow-list.html', **context)


@main.route('/comment-hidden-or-show/<int:id>/')
@permission_required(Permission.MODERATE)
def comment_hidden_or_show(id):
    comment = Comment.query.filter_by(id=id).first()
    action = request.args.get('action')
    if action == 'hidden':
        comment.hidden_comment()
        db.session.commit()
        flash('您已禁止显示该条评论')
    elif action == 'show':
        comment.show_comment()
        db.session.commit()
        flash('您已恢复显示该条评论')
    return redirect(url_for('main.post_detail', id=comment.post_id))
