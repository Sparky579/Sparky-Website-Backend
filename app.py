from flask import Flask, Blueprint
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, declarative_base

from create_app import createApp
from extension import db

from auth.auth import auth_bp
from auth.cookie import cookie_bp
from auth.mail import mail_bp
from chat import chat_bp
import os


app = createApp()
app.register_blueprint(auth_bp)
app.register_blueprint(cookie_bp)
app.register_blueprint(mail_bp)
app.register_blueprint(chat_bp)
current_dir = os.path.dirname(os.path.abspath(__file__))
db_filename = 'database.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(current_dir, db_filename)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Base = declarative_base()
db.init_app(app)
appHasRunBefore:bool = False
@app.before_request
def firstRun():
    global appHasRunBefore
    if not appHasRunBefore:
        db.create_all()
        # Run any of your code here
        # Set the bool to True so this method isn't called again
        appHasRunBefore = True

CORS(app)

@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True)
