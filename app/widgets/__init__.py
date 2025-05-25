from flask import Blueprint

bp = Blueprint('widgets', __name__)

from app.widgets import routes