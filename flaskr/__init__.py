import os

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flaskr.db import get_db, get_url_from_code, insert_url, check_auth, add_admin
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('You need to be logged in to access this page', 'alert-danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='Z9AU72Hp4jVhuLiztqXmPy102kS0qGJU',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    from . import db
    db.init_app(app)

    from . import shorter
    app.register_blueprint(shorter.bp)

    from . import faker
    app.register_blueprint(faker.bp)


    @app.route('/')
    def main():
        return render_template('main.html')
    
    @app.route('/links')
    def links():
        return render_template('links.html')
    
    @app.route('/add-redirect', methods=['POST', 'GET'])
    @login_required
    def add_redirect():
        if request.method == 'POST':
            db = get_db()
            link = request.form['link']
            code = request.form['code']
            if insert_url(link, code) != None:
                flash(f'Link created successfully at <a href="/{code}">https://tokard.dev/{code}</a> !', 'alert-success')
            else:
                flash('Error : maybe this name is already in use or the link is invalid?', 'alert-danger')
            return render_template('add_redirect.html')
        else:
            return render_template('add_redirect.html')


    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            auth = check_auth(username.lower(), password)

            if not auth:
                flash('Invalid username or password', 'alert-danger')
                return redirect(url_for('login'))

            # Si les informations de connexion sont correctes, on connecte l'utilisateur
            session['user'] = username
            return redirect(url_for('main'))

        if 'user' in session:
            return redirect(url_for('main'))

        return render_template('login.html')
    
    @app.route('/logout')
    def logout():
        session.pop('user', None)
        return redirect(url_for('main'))

    return app