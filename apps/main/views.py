import os

from flask import send_from_directory, current_app, render_template

from apps.main import main


@main.route('/')
def index():
    return render_template('main/index.html')


@main.route('/uploads/<path:filename>/')
def get_file(filename):
    return send_from_directory(os.path.join(current_app.config['UPLOAD_FOLDER']), filename)
