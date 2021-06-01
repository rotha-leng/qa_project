from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin

from flask import Flask, render_template, request, session, url_for, redirect, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '!loveyou@ll'


DB_USER = 'postgres'  # database user
DB_PWD = '2001'  # database password
DB_NAME = 'qadb'

app.config['DATABASE_URL'] = "postgresql://%s:%s@localhost:5432/%s" % (DB_USER, DB_PWD, DB_NAME)

login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"


db = SQLAlchemy(app)

from .question import *  # register post view, so that its url is routable

@app.route('/')
def index():
    return render_template('home/index.html')

