import logging
from flask import Blueprint, current_app, g, url_for, redirect, render_template, request, send_from_directory, abort
# from models.storage import queueAlbum
# import models.storage
import json


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
        # task = models.storage.queueAlbum(url, format, thumbnail, autostart)
        task_data = {'url':url, 'format':format, 'thumbnail':thumbnail, 'autostart':autostart}
        redis_manager = current_app.extensions['redis_manager']
        redis = redis_manager.get_redis()
        redis.lpush('albums_task_queue', json.dumps(task_data))
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