from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    # email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
    #                                          Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('保持登录状态')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               ' 用户名支持英文、数字和下划线')])
    password = PasswordField('密码', validators=[
        DataRequired(), EqualTo('password2', message='请确认密码是否一致')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    invitation_code = StringField('邀请码', validators=[DataRequired()])
    submit = SubmitField('注册')

    def validate_email(self, field):
        if User.objects(email=field.data).first():
            raise ValidationError('邮箱已被注册！')

    def validate_username(self, field):
        if User.objects(username=field.data).first():
            raise ValidationError('用户名已被注册')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('旧密码', validators=[DataRequired()])
    password = PasswordField('新密码', validators=[
        DataRequired(), EqualTo('password2', message='两次密码不一致.')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('修改')