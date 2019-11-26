from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import FileField, SubmitField, StringField, TextAreaField, PasswordField, BooleanField
from wtforms.validators import Length, DataRequired, EqualTo, Email, ValidationError

# 注册
from apps.models import User


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 16)])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired(), EqualTo('password2', message='两次密码不一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱已被注册')

    def validate_name(self, field):
        if User.query.filter_by(name=field.data).first():
            raise ValidationError('该用户名已被注册')


# 登录
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登录')
    submit = SubmitField('登录')


# 修改密码
class PasswordChangeForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('password_again', message='两次密码不一致')])
    password_again = PasswordField('重复密码', validators=[DataRequired()])
    submit = SubmitField('确认修改')

    def validate_old_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('旧密码输入错误')

    def validate_new_password(self, field):
        if current_user.verify_password(field.data):
            raise ValidationError('新密码不能和旧密码相同')


# 修改邮箱
class EmailChangeForm(FlaskForm):
    new_email = StringField('新邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    submit = SubmitField('更新Email')

    def validate_new_email(self, field):
        if current_user.email == field.data:
            raise ValidationError('新邮箱不能和旧邮箱相同')

    def validate_password(self, field):
        if not current_user.verify_password(field.data):
            raise ValidationError('密码输入错误')


# 重置密码
class ResetPasswordForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])

    submit = SubmitField('重置密码')

    def validate_email(self, field):
        if not User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱不存在')


# 重置密码
class ResetPasswordForm2(FlaskForm):
    new_password = PasswordField('新密码', validators=[DataRequired(), EqualTo('password_again', message='两次密码不一致')])
    password_again = PasswordField('重复密码', validators=[DataRequired()])

    submit = SubmitField('重置密码')

