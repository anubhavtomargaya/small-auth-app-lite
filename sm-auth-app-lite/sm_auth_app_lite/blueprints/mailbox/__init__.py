from flask import Blueprint

gmail_app = Blueprint('gmail_app', __name__)

from . import routes

