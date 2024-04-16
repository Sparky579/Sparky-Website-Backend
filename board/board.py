from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from extension import db
from auth.auth import User
board_bp = Blueprint('board', __name__)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    message = db.Column(db.String)


def add_message():
    pass


def remove_message():
    pass


