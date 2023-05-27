import datetime

from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField


## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
ckeditor = CKEditor(app)
Bootstrap(app)


##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///posts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    def __init__(self, title, subtitle, date, body, author, img_url):
        self.title = title
        self.subtitle = subtitle
        self.date = date
        self.body = body
        self.author = author
        self.img_url = img_url


##WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


class EditPostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


# @app.route("/post/<int:index>")
# def show_post(index):
#     posts = db.session.query(BlogPost).all()
#     requested_post = None
#     for blog_post in posts:
#         if blog_post.id == index:
#             requested_post = blog_post
#     return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/new-post', methods=['GET', 'POST'])
def add_post():
    form = CreatePostForm()
    if request.method == 'GET':
        return render_template('make-post.html', form=form)
    else:
        if form.validate_on_submit():
            new_post = BlogPost(
                title=form.title.data,
                subtitle=form.subtitle.data,
                author=form.author.data,
                date=datetime.datetime.
                strftime(datetime.datetime.
                         now().date(), "%B %d,%Y"),
                body=form.body.data,
                img_url=form.img_url.data,
            )

            with app.app_context():
                db.session.add(new_post)
                db.session.commit()
            return redirect(url_for('get_all_posts'))


@app.route('/post')
def show_post():
    post_id = request.args.get('index')
    fetched_post = BlogPost.query.get(post_id)
    return render_template('post.html', post=fetched_post)


@app.route('/edit-post', methods=['GET', 'POST'])
def edit_post():
    post_id = request.args.get('post_id')
    fetched_post = BlogPost.query.get(post_id)
    edited_post_form = EditPostForm()
    if request.method == 'GET':
        edited_post_form.title.data = fetched_post.title
        edited_post_form.subtitle.data = fetched_post.subtitle
        edited_post_form.author.data = fetched_post.author
        edited_post_form.img_url.data = fetched_post.img_url
        edited_post_form.body.data = fetched_post.body
        title = 'Edit Post'
        return render_template('make-post.html',
                               form=edited_post_form,
                               title=title)
    else:
        if edited_post_form.validate_on_submit():
            fetched_post.title = edited_post_form.title.data
            fetched_post.subtitle = edited_post_form.subtitle.data
            fetched_post.author = edited_post_form.author.data
            fetched_post.img_url = edited_post_form.img_url.data
            fetched_post.body = edited_post_form.body.data
            db.session.commit()
            return redirect(url_for('show_post', index=post_id))
        else:
            title = 'Edit Post'
            return render_template('make-post.html',
                                   form=edited_post_form,
                                   title=title)


@app.route('/delete')
def delete_post():
    post_id = request.args.get('post_id')
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)