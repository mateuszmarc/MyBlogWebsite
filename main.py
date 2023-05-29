import datetime
import sqlite3

from wtforms.ext import sqlalchemy

from my_forms import CreatePostForm, EditPostForm, RegisterForm
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import login_user, LoginManager, current_user, logout_user,\
    UserMixin
from flask_bcrypt import Bcrypt
import os
import dotenv
from sqlalchemy.exc import OperationalError

## Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

dotenv.load_dotenv('.env')
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('secret_key')
ckeditor = CKEditor(app)
Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)
##CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##CONFIGURE TABLE
class BlogPost(db.Model):
    __tablename__ = 'blog_post'
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


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)


def check_database_table(table):
    try:
        all_records = db.session.query(table).all()
    except OperationalError:
        with app.app_context():
            db.create_all()


@app.route('/')
def get_all_posts():
    check_database_table(BlogPost)
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


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
        check_database_table(User)
        if User.query.filter_by(email=form.email.data):
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


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_user_email = User.query.filter_by(email=form.email.data).first()
            if new_user_email:
                flash('This email is already registered.')
                redirect(url_for('login'))
            else:
                new_user = User()
                new_user.username = form.username.data
                new_user.email = form.email.data
                new_user.password = \
                    bcrypt.generate_password_hash(password=form.password.data,
                                                  rounds=10)
                with app.app_context():
                    db.session.add(new_user)
                    db.session.commit()
                    return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/logout')
def logout():
    return redirect(url_for('get_all_posts'))
if __name__ == "__main__":
    app.run(debug=True)