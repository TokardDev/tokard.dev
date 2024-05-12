import os

from flask import Flask, render_template, request, flash
from flaskr.db import get_db, get_url_from_code, insert_url




def create_app(test_config=None):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
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


    @app.route('/')
    def main():
        return render_template('main.html')
    
    @app.route('/add-redirect', methods=['POST', 'GET'])
    def add_redirect():
        if request.method == 'POST':
            db = get_db()
            link = request.form['link']
            code = request.form['code']
            if insert_url(link, code) != None:
                flash('Link Created', 'alert-success')
            else:
                flash('Error : maybe this name is already used?', 'alert-danger')
            return render_template('add_redirect.html')
        else:
            return render_template('add_redirect.html')


    return app