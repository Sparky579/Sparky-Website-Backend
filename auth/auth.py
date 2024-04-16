# auth.py

from flask import Flask, Blueprint, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from extension import db
from flask_bcrypt import Bcrypt, generate_password_hash, check_password_hash
from sqlalchemy.orm import DeclarativeBase
import random
from auth.mail import CookieMail, check_code_available
import string


class Base(DeclarativeBase):
    pass


auth_bp = Blueprint('auth', __name__)


# db = SQLAlchemy(model_class=Base)

def generate_random_code(length=12):
    """生成指定长度的邀请码"""
    letters_and_digits = string.ascii_letters + string.digits
    code = ''.join(random.choice(letters_and_digits) for _ in range(length))
    return code


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    mail = db.Column(db.String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class InvitationCode(db.Model):
    __tablename__ = 'invitation_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(12), unique=True)
    used = db.Column(db.Boolean, default=False)
    identity = db.Column(db.String(50), nullable=False)


@auth_bp.route('/generate_code', methods=['GET'])
def generate_code():
    form_data = request.args
    cookie = request.cookies.get('user')
    identity = form_data['identity']
    need = form_data['need']
    new_codes = [InvitationCode(cookie=generate_random_code(12), used=False, identity=identity) for _ in range(need)]
    return jsonify({'message': new_codes}), 201


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    mail = data['mail']
    code = data['code']
    cookie = data['cookie']
    # if code != 'ASDFGH654321':
    #     return jsonify({'message': 'Invalid invitation code'}), 400
    existing_user = User.query.filter_by(username=username).first()

    if existing_user:
        return jsonify({'message': 'Username already exists'}), 409

    cookiemail = check_code_available(code, cookie)
    if not cookiemail or cookiemail.value != code:
        return jsonify({'message': 'Authentication wrong'}), 401
    user = User(username=username, mail=mail)
    user.set_password(password)
    db.session.add(user)
    db.session.delete(cookiemail)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        return jsonify({'message': 'Login successful'})
    return jsonify({'message': 'Invalid username or password'}), 401
