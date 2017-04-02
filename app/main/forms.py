#coding:utf-8

from flask_wtf import FlaskForm
from flask_pagedown.fields import PageDownField
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, \
    SelectField, FloatField
from wtforms import ValidationError
from wtforms.validators import Required, Length, Email, Regexp, NumberRange
from ..models import Role, User

class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')

class EditProfileForm(FlaskForm):
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[Required(), Length(1, 64),
                                             Email()])
    username = StringField('Username', validators=[
         Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                           'Usernames must have only letters, '
                                           'numbers, dots or underscores')
    ])
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    body = PageDownField("what's on your mind?", validators=[Required()],
                         render_kw={'rows':5})
    submit = SubmitField('Submit')

class CommentForm(FlaskForm):
    body = StringField('', validators=[Required()])
    submit = SubmitField('Submit')

class AccountForm(FlaskForm):
    goods = StringField('Goods', validators=[Required()])
    price = FloatField('Price', validators=[NumberRange(0, 99999999)])
    use   = SelectField('Use', choices=[(u'吃', u'吃'),
                                        (u'穿', u'穿'),
                                        (u'住', u'住'),
                                        (u'用', u'用'),
                                        (u'行', u'行'),
                                        (u'娱', u'娱'),
                                        (u'其它', u'其它')], validators=[Required()])
    submit = SubmitField('Submit')
