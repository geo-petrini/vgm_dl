import logging
from flask import Blueprint, current_app, g, url_for, redirect, render_template, request, send_from_directory, abort
# from models.storage import queueAlbum
from models.storage import *
import json


bp = Blueprint('api', __name__)


@bp.route('/processurl', methods=['POST'])
def processUrl():
    logging.getLogger('vgmdl').debug(f'request: {request.form}')
    url = request.form.get('url')
    format = request.form.get('format')

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
            status=DOWNLOAD_QUEUED
        )
        db.session.add(album)
        db.session.commit()        
    else:
        abort(400, 'Invalid URL')
    return 'Task submitted successfully'


@bp.route('/albums', methods=['GET'])
def get_albums():
    stmt = db.select(Album).order_by(Album.id.desc())
    records = db.session.execute(stmt).scalars().all()
    # records = Album.query.all()
    out = []
    for record in records:
        out.append( record.to_json() )
    return out

@bp.route('/album/<album_id>', methods=['GET'])
def get_album(album_id):
    album = Album.query.filter_by(id=album_id).first()
    tracks = Track.query.filter(Track.album_id == album.id).all()
    out = album.to_json()   # FIX this does not work as out becomes a string
    out['tracks'] = []
    for track in tracks:
        out['tracks'].append( track.to_json() )
    return out

@bp.route('/album/<album_id>/tracks', methods=['GET'])
def get_album_tracks(album_id):
    tracks = Track.query.filter(Track.album_id == album_id).all()
    out = []
    for track in tracks:
        out.append( track.to_json() )
    return out


@bp.route('/album/<album_id>/track/<track_id>', methods=['GET'])
def get_album_track(album_id, track_id):
    tracks = Track.query.filter( (Track.album_id == album_id) & (Track.id == track_id)).all()
    out = []
    for track in tracks:
        out.append( track.to_json() )
    return out

@bp.route('/track/<track_id>', methods=['GET'])
def get_track(track_id):
    tracks = Track.query.filter(Track.id == track_id).all()
    out = []
    for track in tracks:
        out.append( track.to_json() )
    return out

@bp.route('/album/<album_id>', methods=['DELETE'])
def delete_album(album_id):
    out = ''
    album = None
    tracks = None
    try:
        album = Album.query.filter_by(id=album_id).first()
    except Exception as e:
        logging.getLogger('vgmdl').exception(f'error listing album {album_id}')
        return e, 404
    
    if album:
        try:
            tracks = Track.query.filter(Track.album_id == album.id).all()
        except Exception as e:
            logging.getLogger('vgmdl').exception(f'error listing tracks from album {album_id}')
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