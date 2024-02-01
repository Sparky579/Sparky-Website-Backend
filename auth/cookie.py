from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from extension import db
from auth.auth import User
from sqlalchemy.orm import DeclarativeBase
import random

cookie_bp = Blueprint('cookie', __name__)

class Cookie(db.Model):
    __tablename__ = 'cookies'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    value = db.Column(db.String)
    expires_at = db.Column(db.DateTime)
    user_id = db.Column(db.Integer)


def delete_expired_cookies():
    current = datetime.now()
    db.session.query(Cookie).filter(Cookie.expires_at < current).delete()
    db.session.commit()


@cookie_bp.route('/set_cookie', methods=['POST'])
def set_cookie():
    delete_expired_cookies()
    data = request.get_json()

    # 验证数据
    username = data.get('username')
    password = data.get('password')
    cookie_value = data.get('cookie')
    if not (username and password and cookie_value):
        return jsonify({'message': 'Missing data'}), 400

    user = User.query.filter_by(username=username)
    if user and user.first().check_password(password):
        pass
    else:
        return jsonify({'message': 'Invalid username or password'}), 401

    expires_at = datetime.now() + timedelta(hours=1)

    # 创建并保存 Cookie 实例
    Cookie.query.filter_by(value=cookie_value).delete()
    new_cookie = Cookie(value=cookie_value, expires_at=expires_at, user_id=user.first().id)
    db.session.add(new_cookie)
    db.session.commit()

    # 返回成功响应
    return jsonify({'message': 'Cookie set successfully'}), 201

@cookie_bp.route('/get_account', methods=['POST'])
def get_account_by_cookie():
    delete_expired_cookies()
    data = request.get_json()

    cookie_value = data.get('cookie')
    userid_query = Cookie.query.filter_by(value=cookie_value)
    if userid_query and userid_query.first():
        user = User.query.filter_by(id=userid_query.first().user_id)
        return jsonify({'message': user.first().username}), 200
    else:
        return 'no such user', 400

