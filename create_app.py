from flask import Flask, Blueprint
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, declarative_base
from extension import db


app, limiter = None, None

def createApp():
    global app
    if app:
        return app
    app = Flask(__name__)
    return app

def createLimiter():
    global app
    global limiter
    # print(app, limiter)
    if not app:
        createApp()
    if limiter:
        return limiter
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=[]  # 默认限制: 每分钟1次请求
    )
    return limiter