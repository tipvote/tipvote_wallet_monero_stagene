from flask import Flask
from config import SQLALCHEMY_DATABASE_URI_0
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI_0


db = SQLAlchemy(app)
login_manager = LoginManager(app)