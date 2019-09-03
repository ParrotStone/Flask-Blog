import os
import secrets
from datetime import datetime
# The new renamed module for url manipulations for Python3
from urllib.parse import urlparse, urljoin
from PIL import Image
from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import app, app_bcrypt, db
from flask_blog.forms import RegisterationForm, LoginForm, UpdateAccountForm, PostForm
from flask_blog.models import User, Post


# Display profile picture
def get_img_src():
    # Will return None in case the user is not logged in which will not affect anything since the damn block of navigation doesn't show up unless the user is logged in
    if current_user.is_authenticated:
        if current_user.img_file == 'default.png':
            return url_for('static', filename=f'images/profile_pics/{current_user.img_file}')

        return url_for('static', filename=f'images/profile_pics/{current_user.profile_dir}{current_user.img_file}')

    return None


@app.route('/')
def index():
    posts = Post.query.all()
    return render_template('index.html', page_title='Flask Blog | Welcome!', posts=posts, img_file_src=get_img_src())


@app.route('/about')
def about():
    return render_template('about.html', page_title='Flask Blog | About', img_file_src=get_img_src())


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = RegisterationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_pwd = app_bcrypt.generate_password_hash(
                form.password.data, 13)
            user_path = os.path.join(
                app.root_path, 'static/images/profile_pics/')
            user_dir_name = f'{secrets.token_hex(12)}/'
            full_user_path = f'{user_path}{user_dir_name}'
            os.mkdir(full_user_path)
            user = User(username=form.username.data.strip(),
                        email=form.email.data.lower(), profile_dir=user_dir_name, password=hashed_pwd)

            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))

        flash(f'The submitted data is not corrent. Please enter correct info!', 'failure')

    return render_template('register.html', page_title='Flask Blog | Register', form=form)


# Checking the safety of the URL to prevent open-redirects attacks
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and app_bcrypt.check_password_hash(user.password, form.password.data):
            flash('Logged in successfully!', 'success')
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            # The way down here helps you avoid 'open redirects' attacks by redirecting either to account/index - See the documentation for more details
            # return redirect(f'{next_page}') if is_safe_url(next_page) else redirect(url_for('index'))
            # Another way using the is_safe_url() function which was written by the Flask creator, it checks that the redirect to URL is a path on the main URL/host_url, If it exists it will route to it, otherwise throw the 404 error & the next_page check here is to ensure that the client doesn't get redirected to /None path(valid path if not check though), This is super nice and helps prevent the open-redirects attacks ;)
            return redirect(f'{next_page}') if next_page and is_safe_url(next_page) else redirect(url_for('index'))
        flash('Login Unsuccessful. Please check email address and password', 'failure')
    return render_template('login.html', page_title='Flask Blog | Login', form=form)


def save_picture(form_img):
    random_hex_name = secrets.token_hex(10)
    _, img_ex = os.path.splitext(form_img.filename)
    new_img_name = f'{random_hex_name}{img_ex}'
    new_img_path = os.path.join(
        app.root_path, f'static/images/profile_pics/{current_user.profile_dir}', new_img_name)

    output_size = (130, 130)
    new_img = Image.open(form_img)
    new_img.thumbnail(output_size)
    new_img.save(new_img_path)

    return new_img_name


# Auto-cleaning function for the user old profile pics
def clean_old_pictures():
    pictures_path = os.path.join(
        app.root_path, f'static/images/profile_pics/{current_user.profile_dir}')
    pictures = os.listdir(pictures_path)
    current_user_img = current_user.img_file

    for picture in pictures:
        if picture != current_user_img:
            os.remove(f'{pictures_path}{picture}')


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()

    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.brief_info.data = current_user.brief_info

    if form.validate_on_submit():
        # Strip() function down here ensures that NO whitespace will be prepended or appended to the fields's value
        is_info_changed = (current_user.username != form.username.data.strip() or current_user.email.strip() !=
                           form.email.data or current_user.brief_info != form.brief_info.data.strip() or form.img.data)

        if is_info_changed:
            current_user.username = form.username.data.strip()
            current_user.email = form.email.data.strip().lower()
            current_user.brief_info = form.brief_info.data.strip()

            if form.img.data:
                current_user.img_file = save_picture(form.img.data)
                clean_old_pictures()

            db.session.commit()
            flash('Account information has been updated successfully!', 'success')
        else:
            flash('Nothing was updated, hence, nothing changed!', 'info')
        return redirect(url_for('account'))
    return render_template('account.html', page_title='Account', img_file_src=get_img_src(), form=form)


@app.route('/post/new', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(title=form.title.data,
                        content=form.content.data, date_updated=None, author=current_user)
        db.session.add(new_post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('index'))
    return render_template('create_post.html', page_title='New Post', form=form, img_file_src=get_img_src())


@app.route('/post/<int:post_id>')
def post(post_id):
    user_post = Post.query.get_or_404(post_id)
    return render_template('post.html', page_title=user_post.title, post=user_post, img_file_src=get_img_src())


@app.route('/post/<int:post_id>/update', methods=['GET', 'POST'])
@login_required
def update_post(post_id):
    form = PostForm()
    user_post = Post.query.get_or_404(post_id)

    if user_post.author != current_user:
        abort(403)

    if request.method == 'GET':
        form.title.data = user_post.title
        form.content.data = user_post.content

    if form.validate_on_submit():
        user_post.title = form.title.data
        user_post.content = form.content.data
        user_post.date_updated = datetime.now()
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect(url_for('index'))

    return render_template('update_post.html', page_title='Update Post', form=form, img_file_src=get_img_src())


@app.route('/post/<int:post_id>/delete', methods=['POST'])
@login_required
def delete_post(post_id):
    user_post = Post.query.get_or_404(post_id)

    if user_post.author != current_user:
        abort(403)

    db.session.delete(user_post)
    db.session.commit()
    flash('Your Post Has Been Deleted Successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
