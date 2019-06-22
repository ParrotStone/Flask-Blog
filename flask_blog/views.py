from flask import render_template, request, flash, redirect, url_for
from flask_blog import app
from flask_blog.forms import RegisterationForm, LoginForm
from flask_blog.models import User, Post


posts = [
    {
        'author': 'Abdulrahman Ali',
        'title': 'First Article',
        'content': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Et praesentium vel, sint consequuntur nihil enim earum in! Vel exercitationem animi eveniet harum minus nemo autem necessitatibus, iste officia debitis odit?',
        'date_created': 'October, 12 2019'
    },
    {
        'author': 'Jane Doe',
        'title': 'Second Article',
        'content': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Et praesentium vel, sint consequuntur nihil enim earum in! Vel exercitationem animi eveniet harum minus nemo autem necessitatibus, iste officia debitis odit?',
        'date_created': 'October, 15 2019'
    },
    {
        'author': 'John Smith',
        'title': 'Third Article',
        'content': 'Lorem ipsum, dolor sit amet consectetur adipisicing elit. Et praesentium vel, sint consequuntur nihil enim earum in! Vel exercitationem animi eveniet harum minus nemo autem necessitatibus, iste officia debitis odit?',
        'date_created': 'March, 12 2019'
    }
]


@app.route('/')
def index():
    return render_template('index.html', page_title='Flask Blog | Welcome!', posts=posts)


@app.route('/about')
def about():
    return render_template('about.html', page_title='Flask Blog | About')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash(f'Account created for {form.username.data}!', 'success')
            return redirect(url_for('login'))
        flash(
            f'The submitted data is not corrent, Enter correct info!', 'failure')

    return render_template('register.html', page_title='Flask Blog | Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == 'admin@mail.com' and form.password.data == 'password':
            flash('You have been logged in!', 'success')
            return redirect(url_for('index'))
        flash('Login Unsuccessful. Please check email address and password', 'failure')
    return render_template('login.html', page_title='Flask Blog | Login', form=form)
