import datetime
from flask_gravatar import Gravatar
from functools import wraps
from sqlalchemy.orm import relationship
from my_forms import CreatePostForm, EditPostForm, RegisterForm, LoginForm, CommentForm
from flask import Flask, render_template, redirect, url_for, request, flash, abort
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_ckeditor import CKEditor
from flask_login import login_user, LoginManager, current_user, logout_user, \
    UserMixin, login_required
from flask_bcrypt import Bcrypt
import os
import dotenv
from sqlalchemy.exc import OperationalError

# Delete this code:
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
# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

gravatar = Gravatar(app,
                    size=1000,
                    rating='g',
                    default='retro',
                    force_default=False,
                    force_lower=False,
                    use_ssl=False,
                    base_url=None)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def admin_only(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if current_user.id == 1:
            return f(*args, **kwargs)
        else:
            return abort(403)
    return wrap


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    posts = relationship("BlogPost", back_populates="author")
    comments = relationship("Comment", back_populates="comment_author")

    def __repr__(self):
        return f'{self.username}'


# CONFIGURE TABLE
class BlogPost(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # we have to link BlogPost to the User( refer to primary key of the User)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="parent_post")

    def __repr__(self):
        return f'Post "{self.id}"'


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(1000), nullable=False)

    post_id = db.Column(db.Integer, db.ForeignKey("posts.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_post = relationship("BlogPost", back_populates="comments")
    comment_author = relationship("User", back_populates="comments")

    def __repr__(self):
        return f"{self.id}"


# def check_database_table(table):
#     try:
#         all_records = db.session.query(table).all()
#     except OperationalError:
#         with app.app_context():
#             db.create_all()
db.create_all()


@app.route('/')
def get_all_posts():
    # check_database_table(BlogPost)
    posts = db.session.query(BlogPost).all()
    admin = False
    if current_user.is_authenticated and current_user.id == 1:
        admin = True
    return render_template("index.html", all_posts=posts,
                           logged_in=current_user.is_authenticated,
                           admin=admin)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route('/new-post', methods=['GET', 'POST'])
@login_required
@admin_only
def add_post():
    form = CreatePostForm()
    if request.method == 'GET':
        return render_template('make-post.html', form=form)
    else:
        # check_database_table(User)
        new_post = BlogPost()
        new_post.title = form.title.data
        new_post.subtitle = form.subtitle.data
        # new_post.author = form.author.data
        new_post.date = datetime.datetime.\
            strftime(datetime.datetime.now().date(), "%B %d, %Y")
        new_post.body = form.body.data
        new_post.img_url = form.img_url.data
        # new_post.author_id = current_user.id
        new_post.author = current_user


        with app.app_context():
            db.session.add(new_post)
            db.session.commit()
        return redirect(url_for('get_all_posts'))


@app.route('/post', methods=['GET', 'POST'])
def show_post():
    form = CommentForm()
    post_id = request.args.get('index')
    admin = False
    fetched_post = BlogPost.query.filter_by(id=post_id).first()
    if request.method == 'POST':
        if form.validate_on_submit():
            if current_user.is_authenticated:
                new_comment = Comment()
                new_comment.text = form.body.data
                new_comment.post_id = post_id
                new_comment.author_id = current_user.id
                new_comment.comment_author = current_user
                new_comment.parent_post = fetched_post
                db.session.add(new_comment)
                db.session.commit()
                if current_user.id == 1:
                    admin = True
                return render_template('post.html', admin=admin,
                                       post=fetched_post, form=form)

            else:
                flash("You have to log in to leave comments.")
                return redirect(url_for('login'))


    else:
        if current_user.is_authenticated and current_user.id == 1:
            admin = True
        fetched_post = BlogPost.query.filter_by(id=post_id).first()
        comments = fetched_post.comments
        return render_template('post.html',
                               post=fetched_post,
                               admin=admin,
                               form=form)


@app.route('/edit-post', methods=['GET', 'POST'])
@admin_only
def edit_post():
    post_id = request.args.get('post_id')
    fetched_post = BlogPost.query.get(post_id)
    edited_post_form = EditPostForm()
    if request.method == 'GET':
        edited_post_form.title.data = fetched_post.title
        edited_post_form.subtitle.data = fetched_post.subtitle
        # edited_post_form.author.data = fetched_post.author
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
            # fetched_post.author = edited_post_form.author.data
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
@login_required
@admin_only
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
            new_user_by_email = User.query.filter_by(email=form.email.data).first()
            new_user_by_username =\
                User.query.filter_by(username=form.username.data).first()
            if new_user_by_email:
                flash('This email is already registered.')
                return redirect(url_for('login'))
            elif new_user_by_username:
                flash('This username is not available.')
                return redirect(url_for('register'))
            else:
                new_user = User()
                new_user.username = form.username.data
                new_user.email = form.email.data
                new_user.password = \
                    bcrypt.generate_password_hash(password=form.password.data,
                                                  rounds=10)

                db.session.add(new_user)
                db.session.commit()
                login_user(new_user)
                return redirect(url_for('get_all_posts'))
    return render_template("register.html", form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('get_all_posts'))
            else:
                flash("Password is incorrect.")
                return redirect(url_for('login'))
        else:
            flash("There is no such email registered.")
            return redirect(url_for('login'))
    else:
        return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('get_all_posts'))


if __name__ == "__main__":
    app.run(debug=True)