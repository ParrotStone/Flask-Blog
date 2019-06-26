import secrets
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(20)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app_bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# To avoid the circular import issues
from flask_blog import views
