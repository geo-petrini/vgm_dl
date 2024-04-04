import logging
from flask import url_for, redirect, render_template, request, Blueprint, send_from_directory, abort
# from models.storage import queueAlbum
import models.storage

bp = Blueprint('default', __name__)

@bp.route('/')
def home():
    return redirect(url_for('default.index'))

@bp.route('/index')
def index():
    content = ''
    return render_template("index.html", data=content, title='Video Game Music Downloader')

@bp.route('/processurl', methods=['POST'])
def processUrl():
    logging.getLogger('vgmdl').debug(f'request: {request.form}')
    url = request.form.get('url')
    format = request.form.get('format')
    thumbnail = request.form.get('thumbnail') == 'true'  # Convert 'true' to True, 'false' to False
    autostart = request.form.get('autoStart') == 'true'  # Convert 'true' to True, 'false' to False
    if url != None and format != None:
        # Save task to the database
        task = models.storage.queueAlbum(url, format, thumbnail, autostart)
    else:
        abort(400, 'Invalid URL')
    return 'Task submitted successfully'

@bp.route('/status', methods=['GET'])
def get_status():
    pass    

@bp.route('/css/<theme>/<path:filename>')  # the "theme" folder does not exist but is there for routing and masking purpose
def serve_theme_css(theme, filename):
    if theme == 'bootstrap':
        return send_from_directory('static/css', f'bootstrap.min.css')
    else:
        return send_from_directory('static/css', f'bootstrap-{theme}.min.css')