# coding=utf-8
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, BooleanField
from pymongo import MongoClient
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from flask_pagedown.fields import PageDownField
from flask_wtf.file import FileField, FileRequired, FileAllowed
from flask_uploads import UploadSet, configure_uploads, IMAGES, patch_request_class


class EditProfileForm(FlaskForm):
    name = StringField(u'姓名', validators=[Length(0, 64)])
    # location = SelectField('地址', choices=Province_choice)
    about_me = TextAreaField('自我介绍', validators=[Length(0, 64)])
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    choices = [('Administrator', '管理员'), ('Moderator', '协管员'), ('User', '用户')]
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64),
                                          Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                              '支持英文和字母下划线.')])
    activate = BooleanField('账户激活状态')
    role = SelectField('权限', choices=choices)
    name = StringField('姓名', validators=[Length(0, 64)])
    location = StringField('地址', validators=[Length(0, 64)])
    about_me = TextAreaField('自我介绍')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate_email(self, field):
        if field.data == self.user.username:
            return
        if MongoClient().blog.User.find_one({'temp': field.data}):
            raise ValidationError('邮箱已被注册.')

    def validate_username(self, field):
        if field.data == self.user.username:
            return
        if MongoClient().blog.User.find_one({'username': field.data}):
            raise ValidationError('用户名已被注册.')




class EditPostForm(FlaskForm):
    body = PageDownField('', validators=[DataRequired()])
    submit = SubmitField('修改')


class CommentForm(FlaskForm):
    comment = StringField('', validators=[DataRequired()])
    submit = SubmitField('发布')


class MomentForm(FlaskForm):
    photo = FileField(validators=[
        FileAllowed(UploadSet('photos', IMAGES), u'请上传图片哟'),
        FileRequired(u'图片')])
    content = TextAreaField('美食每刻', validators=[DataRequired()],render_kw={'class': 'post-moment', 'rows': 5, 'placeholder': u'这一刻的美食感受...'})
    submit = SubmitField(u'发布')
