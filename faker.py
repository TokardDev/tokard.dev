import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db, get_url_from_code, insert_url

bp = Blueprint('faker', __name__, url_prefix='/')


@bp.route('/faker/')
def faker():
    return render_template('faker.html')