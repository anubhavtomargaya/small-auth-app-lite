from flask import Blueprint

gmail_bp = Blueprint('gmail_bp', __name__)

from . import routes 