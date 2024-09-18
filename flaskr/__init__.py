import os

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flaskr.db import get_db, insert_url, check_auth, get_commissions, get_commissions, get_url_from_code
from functools import wraps
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = './flaskr/static/comms'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}

def generate_unique_id():
    while True:
        id_nbr = ''.join(random.choices(string.digits, k=11))
        if checkIDNbr(id_nbr):
            return id_nbr

def generate_mrz_line_1(id_nbr, person_data):
    return f"IDFR{person_data['last_name'][:5].upper():<5}{person_data['first_name'][:5].upper():<5}{id_nbr}"

def generate_mrz_line_2(person_data):
    birth_date = person_data['birth_date'].replace("-", "")  # Format AAAAMMJJ
    gender = 'N'
    return f"{birth_date}{gender}{random.choices(string.digits, k=3).upper()}"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            flash('You need to be logged in to access this page', 'alert-danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

commissions = []

def update_commissions():
    global commissions
    commissions = get_commissions()

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

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    from . import db
    db.init_app(app)

    app.app_context().push()

    from . import shorter
    app.register_blueprint(shorter.bp)

    from . import faker
    app.register_blueprint(faker.bp)

    @app.route('/')
    def main():
        # if connected, render main, if not render links
        if 'user' in session:
            return render_template('main.html')
        else:
            return render_template('links.html')

    @app.route('/get-nsfw')
    def get_nsfw():
        if request.headers.get('HX-Request'):
            return """
            <link rel="stylesheet" href="static/css/backgrounddance.css">
    <div class="context" style="z-index: 1; height: 100%; width: 100%; background-color: rgba(0, 0, 0, 0)"" >
            <div class="container d-flex justify-content-center align-items-center" style="height: 100vh;">
                <div class="card" style="width: 100%; margin-bottom: 60px; background: rgba(255, 255, 255, 0); border-radius: 0px; box-shadow: 0 4px 30px rgba(0, 0, 0, 0.0); backdrop-filter: blur(0px);">
                    <img src="/static/imgs/tokared.png" class="card-img-top" alt="logo" draggable="false">
                </div>
            </div>
        </div>
        <script>
                var audio = new Audio('static/t.mp3');
                audio.loop = true;
                audio.play();

        </script>
        <div class="area" >
            <ul class="copper">
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    <li></li>
                    
            </ul>
        </div >"""
        else:
            return redirect('/nsfw')
    
    @app.route('/links')
    def links():
        return render_template('links.html')
    
    @app.route('/commissions')
    def comms():
        if commissions == [] :
            update_commissions()

        return render_template('commissions.html', comms=commissions)
    
    @app.route('/nsfw')
    def dance():
        return render_template('dance.html')
    
    @app.route('/delete', methods=['POST'])
    @login_required
    def delete_comms():
        if request.method == 'POST':
            id = request.form['id']
            db.delete_commission(id)
            update_commissions()
            return redirect(url_for('comms'))
        else:
            return redirect(url_for('comms'))
    
    @app.route('/add-commissions', methods=['POST', 'GET'])
    @login_required # utilise db.add_commission(price, description, image, titre)
    def add_commissions():
        if request.method == 'POST':
            if 'price' in request.form and 'description' in request.form and 'titre' in request.form and 'file' in request.files:
                price = request.form['price']
                description = request.form['description']
                titre = request.form['titre']
                file = request.files['file']
                if file.filename == '':
                    flash('No selected file', 'alert-danger')
                    return redirect(request.url)
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)

                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))


                    db.add_commission(price, description, filename, titre)
                    flash('Commission added successfully', 'alert-success')
                    update_commissions()
                    return redirect(url_for('add_commissions'))
            else:
                flash('All fields are required', 'alert-danger')
                return redirect(request.url)

        else:
            return render_template('addcomm.html')

    
    
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
    
    @app.route('/search')
    def search():
        return render_template('search.html')

    @app.route('/api/telerts/generate-card', methods=['POST'])
    def generateCard():
        person_data = request.json

        # Générer un numéro d'identité unique
        id_nbr = generate_unique_id()

        # Générer les lignes MRZ
        mrz_line_1 = generate_mrz_line_1(id_nbr, person_data)
        mrz_line_2 = generate_mrz_line_2(person_data)

        # Retourner le résultat en JSON
        return jsonify({
            'id_nbr': id_nbr,
            'mrz_line_1': mrz_line_1,
            'mrz_line_2': mrz_line_2
        })



    return app
