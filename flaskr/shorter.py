import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db, get_url_from_code, insert_url

bp = Blueprint('shorter', __name__, url_prefix='/')


@bp.route('/<url_code>')
def redirect_url(url_code):
    db = get_db()
    result = get_url_from_code(url_code)
    if result is not None:
        return redirect(result)