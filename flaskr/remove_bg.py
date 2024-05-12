import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db, get_url_from_code, insert_url

from rembg import remove

from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename

import os

bp = Blueprint('remove_bg', __name__, url_prefix='/')


UPLOAD_FOLDER = 'remove_bg/input/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/remove-bg', methods=['POST', 'GET'])
def redirect_url():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            
            input_path = 'remove_bg/input/'+filename
            output_path = 'remove_bg/output/img.png'

            with open(input_path, 'rb') as i:
                with open(output_path, 'wb') as o:
                    input = i.read()
                    output = remove(input)
                    o.write(output)
            return "removed"
    return render_template('remove_bg_form.html')
