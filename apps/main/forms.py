from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed
from wtforms import StringField, TextAreaField, FileField, SubmitField, BooleanField, SelectField
from wtforms.validators import Length, DataRequired, Email, ValidationError

from apps.models import User, Role


class EditProfileForm(FlaskForm):
    nickname = StringField('昵称', validators=[Length(max=16)])
    location = StringField('所在地', validators=[Length(max=64)])
    about_me = TextAreaField('关于自己')
    avatar = FileField('头像', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message="只允许传指定的文件！")])
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 16)])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    confirmed = BooleanField('激活状态')
    role_id = SelectField('用户角色', coerce=int)
    nickname = StringField('昵称', validators=[Length(max=16)])
    location = StringField('所在地', validators=[Length(max=64)])
    about_me = TextAreaField('关于自己')
    avatar = FileField('头像', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], message="只允许传指定的文件！")])
    submit = SubmitField('提交')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first() and self.email.data != field.data:
            raise ValidationError('该邮箱已被注册')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first()and self.username.data != field.data:
            raise ValidationError('该用户名已被注册')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.role_id.choices = [(role.id, role.name) for role in Role.query.all()]
