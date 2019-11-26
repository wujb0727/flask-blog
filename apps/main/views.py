import os
import uuid

from flask import send_from_directory, current_app, render_template, flash, redirect, url_for
from flask_login import login_required, current_user

from apps import db
from apps.decorators import admin_required
from apps.main import main
from apps.main.forms import EditProfileForm, EditProfileAdminForm
from apps.models import User


def random_filename(filename):
    ext = os.path.splitext(filename)[1]
    new_filename = uuid.uuid4().hex + ext
    return new_filename


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/uploads/<path:filename>/')
def get_file(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER']), filename)


@main.route('/user/<int:id>/')
def user(id):
    user = User.query.filter_by(id=id).first_or_404()
    return render_template('main/user.html', user=user)


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
