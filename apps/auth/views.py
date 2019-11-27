from flask import render_template, current_app, flash, redirect, url_for, request
from flask_login import current_user, login_user, login_required, logout_user

from apps import db
from apps.auth import auth
from apps.auth.forms import RegisterForm, LoginForm, PasswordChangeForm, EmailChangeForm, ResetPasswordForm, \
    ResetPasswordForm2
from apps.main.mail import send_mail
from apps.models import User


@auth.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower(), password=form.password.data)
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('注册失败,请重试')
            return render_template('auth/register.html', form=form)
        token = user.generate_confirmation_token()
        send_mail(user.email, '激活账号', 'mail/confirm', user=user, token=token, email=user.email)
        flash('一封确认邮件已经发送到您的邮箱，请及时激活账号！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('您已成功激活您的账号！')
    else:
        flash('激活链接无效或已过期！')
    return redirect(url_for('main.index'))


@auth.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is not None and user.verify_password(form.password.data):
            user.set_last_seen()
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                return redirect(url_for('main.index'))
            return redirect(next)
        flash('用户名或密码错误')
    return render_template('auth/login.html', form=form)


@auth.route('/logout/', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('您已成功登出')
    return redirect(url_for('main.index'))


@auth.route('/password_change/', methods=['GET', 'POST'])
@login_required
def password_change():
    form = PasswordChangeForm()
    if form.validate_on_submit():
        user = current_user
        user.password = form.new_password.data
        try:
            db.session.add(user)
            db.session.commit()
            flash('修改成功,请重新登录')
        except:
            db.session.rollback()
            flash('修改失败,请重新修改')
        logout_user()
        return redirect(url_for('auth.login'))
    return render_template('auth/password_change.html', form=form)


@auth.route('/email_change/', methods=['GET', 'POST'])
@login_required
def email_change():
    form = EmailChangeForm()
    if form.validate_on_submit():
        user = current_user
        token = user.generate_confirmation_token()
        send_mail(form.new_email.data, '确认您的邮箱地址', 'mail/change_email', user=user, token=token,
                  email=form.new_email.data)
        flash('一封确认您新邮箱的邮件已经发送到您新的邮箱，确认后即可使用新邮箱.')
        return redirect(url_for('main.index'))
    return render_template('auth/email_change.html', form=form)


@auth.route('/change_email/<token>')
@login_required
def confirm_email(token):
    if current_user.confirm(token):
        user = current_user
        user.email = request.args.get('email')
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('修改失败,请重新修改')
        db.session.commit()
        flash('您已成功激活您的新邮箱！')
    else:
        flash('激活链接无效或已过期！')
    return redirect(url_for('main.index'))


@auth.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        current_app.user = user
        token = user.generate_confirmation_token()
        send_mail(user.email, '重置密码', 'mail/reset_password', user=user, token=token, email=user.email)
        flash('一封重置密码的邮件已经发送到您的邮箱，确认后即可重置密码.')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset_password/<token>')
def confirm_password(token):
    if current_app.user.confirm(token):
        db.session.commit()
        flash('请重置您的密码！')
    else:
        flash('激活链接无效或已过期！')
    return redirect(url_for('auth.reset_password2'))


@auth.route('/reset_password2/', methods=['GET', 'POST'])
def reset_password2():
    form = ResetPasswordForm2()
    if form.validate_on_submit():
        user = current_app.user
        user.password = form.new_password.data
        try:
            db.session.add(user)
            db.session.commit()
        except:
            db.session.rollback()
            flash('修改失败,请重新修改')
            return render_template('auth/reset_password2.html', form=form)
        flash('重置密码成功')
        return redirect(url_for('main.index'))
    return render_template('auth/reset_password2.html', form=form)
