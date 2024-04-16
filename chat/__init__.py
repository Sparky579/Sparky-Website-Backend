from flask import Blueprint

chat_bp = Blueprint('chat', __name__)
from . import stream_chat
from . import question
