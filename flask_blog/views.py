import os
import secrets
from PIL import Image
from flask import render_template, request, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from flask_blog import app, app_bcrypt, db
from flask_blog.forms import RegisterationForm, LoginForm, UpdateAccountForm
from flask_blog.models import User, Post


posts = [
    {
        'author': 'Abdulrahman Ali',
        'title': 'First Article',
        'content': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Et praesentium vel, sint consequuntur nihil enim earum in! Vel exercitationem animi eveniet harum minus nemo autem necessitatibus, iste officia debitis odit?',
        'date_created': 'October 12, 2019'
    },
    {
        'author': 'Jane Doe',
        'title': 'Second Article',
        'content': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Et praesentium vel, sint consequuntur nihil enim earum in! Vel exercitationem animi eveniet harum minus nemo autem necessitatibus, iste officia debitis odit?',
        'date_created': 'October 15, 2019'
    },
    {
        'author': 'John Smith',
        'title': 'Third Article',
        'content': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Et praesentium vel, sint consequuntur nihil enim earum in! Vel exercitationem animi eveniet harum minus nemo autem necessitatibus, iste officia debitis odit?',
        'date_created': 'March 12, 2019'
    }
]


# Displaying profile picture
def get_img_src():
    # Will return None in case the user is not logged in which will not affect anything since the damn block of navigation doesn't show up unless the user is logged in
    if current_user.is_authenticated:
        if current_user.img_file == 'default.png':
            return url_for('static', filename=f'images/profile_pics/{current_user.img_file}')

        return url_for('static', filename=f'images/profile_pics/{current_user.profile_dir}/{current_user.img_file}')

    return None


@app.route('/')
def index():
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
                form.password.data, 13).decode('utf-8')
            user_path = os.path.join(
                app.root_path, 'static/images/profile_pics/')
            user_filename = secrets.token_hex(12)
            full_user_path = f'{user_path}{user_filename}'
            os.mkdir(full_user_path)
            user = User(username=form.username.data.strip(),
                        email=form.email.data.lower(), profile_dir=user_filename, password=hashed_pwd)

            db.session.add(user)
            db.session.commit()
            flash(f'Your account has been created! You are now able to log in', 'success')
            return redirect(url_for('login'))

        flash(f'The submitted data is not corrent. Please enter correct info!', 'failure')

    return render_template('register.html', page_title='Flask Blog | Register', form=form)


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
            return redirect(url_for('account')) if next_page else redirect(url_for('index'))
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
        app.root_path, f'static/images/profile_pics/{current_user.profile_dir}/')
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


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
