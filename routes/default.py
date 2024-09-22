import logging
from flask import Blueprint, current_app, g, url_for, redirect, render_template, request, send_from_directory, abort
# from models.storage import queueAlbum
from models.storage import *
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
    thumbnail = None
    autostart = True
    # thumbnail = request.form.get('thumbnail') == 'true'  # Convert 'true' to True, 'false' to False
    # autostart = request.form.get('autoStart') == 'true'  # Convert 'true' to True, 'false' to False
    if url != None and format != None:
        # Save task to the database
        # task = models.storage.queueAlbum(url, format, thumbnail, autostart)
        # task_data = {'url':url, 'format':format, 'thumbnail':thumbnail, 'autostart':autostart}
        # redis_manager = current_app.extensions['redis_manager']
        # redis = redis_manager.get_redis()
        # redis.lpush('albums_task_queue', json.dumps(task_data))
        # ch = current_app.cache
        # cache.set('albums_task_queue', json.dumps(task_data))
        album = Album(
            url=url,
            format=format,
        )
        db.session.add(album)
        db.session.commit()        
    else:
        abort(400, 'Invalid URL')
    return 'Task submitted successfully'


@bp.route('/albums', methods=['GET'])
def get_albums():
    records = Album.query.all()
    out = []
    for record in records:
        out.append( record.to_json() )
    return out

@bp.route('/album/<id>', methods=['GET'])
def get_album(id):
    album = Album.query.filter_by(id=uuid.UUID(id)).first()
    tracks = Track.query.filter(Track.album_id == album.id).all()
    out = album.to_json()   # FIX this does not work as out becomes a string
    out['tracks'] = []
    for track in tracks:
        out['tracks'].append( track.to_json() )
    return out

@bp.route('/album/<id>/tracks', methods=['GET'])
def get_album_tracks(id):
    tracks = Track.query.filter(Track.album_id == uuid.UUID(id)).all()
    out = []
    for track in tracks:
        out.append( track.to_json() )
    return out

@bp.route('/album/<id>', methods=['DELETE'])
def delete_album(id):
    out = ''
    album = None
    tracks = None
    try:
        album = Album.query.filter_by(id=uuid.UUID(id)).first()
    except Exception as e:
        return e, 404
    
    try:
        tracks = Track.query.filter(Track.album_id == album.id).all()
    except Exception as e:
        return e, 500

    if tracks:        
        for track in tracks:
            db.session.delete(track)
            db.session.commit()

    if album:
        db.session.delete(album)
        db.session.commit()
    out = 'ok'
    return out, 200

@bp.route('/status', methods=['GET'])
def get_status():
    pass    

@bp.route('/css/<theme>/<path:filename>')  # the "theme" folder does not exist but is there for routing and masking purpose
def serve_theme_css(theme, filename):
    if theme == 'bootstrap':
        return send_from_directory('static/css', f'bootstrap.min.css')
    else:
        return send_from_directory('static/css', f'bootstrap-{theme}.min.css')