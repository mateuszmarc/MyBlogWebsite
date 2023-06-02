from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField
from wtforms.validators import DataRequired, URL, Length
from flask_ckeditor import CKEditorField
from wtforms.fields.html5 import EmailField


class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    # author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class EditPostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    # author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class RegisterForm(FlaskForm):
    username = StringField('Login Name', validators=[DataRequired(),
                                                     Length(min=6, max=30)])
    email = EmailField('Email', validators=[DataRequired(),
                                            Length(min=5, max=100)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=6, max=1000)])
    submit = SubmitField('Sign in')


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(),
                                            Length(min=6, max=100)])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     Length(min=6, max=1000)])
    submit = SubmitField('Log In')


class CommentForm(FlaskForm):
    body = CKEditorField('Comment', validators=[DataRequired()])
    submit = SubmitField("Submit Comment")