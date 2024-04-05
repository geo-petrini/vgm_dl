import logging
from time import sleep
# from sqlalchemy import or_
from flask import current_app
from models.storage import *
from vgmdl import VGMPageParser
import redis
from urllib.parse import unquote
import urllib
import uuid
import json
import os
import re

rd = redis.Redis(host='rpi', port=6379, db=0)


def worker(app):
    with app.app_context():
        while True:
            # Dequeue album task data from Redis list
            json_album_task_data = rd.rpop('albums_task_queue')
            if json_album_task_data:
                album_task_data = json.loads(json_album_task_data)
                logging.getLogger('vgmdl').debug(
                    f"processing task: {album_task_data}")
                read_album(album_task_data)

            # Dequeue track task data from Redis list
            json_track_task_data = rd.rpop('tracks_task_queue')
            if json_track_task_data:
                track_task_data = json.loads(json_track_task_data)
                logging.getLogger('vgmdl').debug(
                    f"processing task: {track_task_data}")
                download_track(track_task_data)

            sleep(1)


def read_album(task):
    parser = VGMPageParser(task['url'])

    album = Album(
        id=uuid.uuid4(),
        url=task['url'],
        title=parser.get_albun_title(),
        format=task['format']
    )
    db.session.add(album)
    db.session.commit()
    track_urls = parser.get_links()
    add_tracks_tasks(album, track_urls)


def add_tracks_tasks(album, track_urls):
    for track_url in track_urls:
        if track_url.endswith(album.format) or album.format == 'all':
            try:
                track = Track(
                    id=uuid.uuid4(),
                    url=track_url,
                    title=unquote(track_url.split('/')[-1]),
                    album_id=album.id
                )
                db.session.add(track)
                db.session.commit()

                logging.getLogger('vgmdl').debug(
                    f'saved track {track.id} for album {album.id}')

                task_data = {'url': track_url, 'track': track.id.hex}
                rd.lpush('tracks_task_queue', json.dumps(task_data))

                logging.getLogger('vgmdl').debug(f'saved task {task_data}')
            except Exception as e:
                logging.getLogger('vgmdl').exception(
                    f'error processing album track {track_url}')


def clean_path(path):
    invalid_chars = ['\\',  '/',  ':', '*',  '?',  '"',  '<',  '>',  '|']
    for ic in invalid_chars:
        while ic in path:
            path = path.replace(ic, ' ')
    path = re.sub('\s+', ' ', path)
    return path


def create_album_folder_path(album_folder):
    folder_path = None
    try:
        folder_path = os.path.join(
            current_app.config['DOWNLOAD_FOLDER'], album_folder)
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # folder already exists, maybe log something
            pass
        else:
            logging.getLogger('vgmdl').debug(
                f'creating album folder {folder_path}')
            os.makedirs(os.path.dirname(folder_path), exist_ok=True)
    except Exception as e:
        logging.getLogger('vgmdl').exception(
            f'could not create path for album with folder "{album_folder}"')

    if not os.path.exists(folder_path):
        logging.getLogger('vgmdl').error(
            f'album folder not present: "{folder_path}"')
        folder_path = None

    return folder_path


def _prepare_download(track, album):
    # track = Track.query.get(  uuid.UUID(track_task['track']) )
    if not track or not album:
        logging.getLogger('vgmdl').error(
            f'invalid track {track.id} and album {album.id} combination')
        return None
    else:
        logging.getLogger('vgmdl').debug(
            f'loaded track {track.id} and album {album.id}')

    album_folder = clean_path(album.title)
    filename = clean_path(track.title)
    logging.getLogger('vgmdl').debug(f'album_folder: {album_folder}')
    logging.getLogger('vgmdl').debug(f'filename: {filename}')

    # manage download paths
    file_path = None
    folder_path = create_album_folder_path(album_folder)
    # logging.getLogger('vgmdl').debug(f'folder_path {folder_path}')
    if folder_path:
        file_path = os.path.join(folder_path, filename)

    return file_path


def download_track(track_task):
    track = Track.query.filter_by(id=uuid.UUID(track_task['track'])).first()
    album = Album.query.get(track.album_id)
    file_path = _prepare_download(track, album)

    if file_path:
        try:
            url = track.url

            filename = os.path.basename(file_path)

            response = urllib.request.urlopen(url)
            file_size = int(response.headers['Content-Length'])
            downloaded_bytes = 0

            logging.getLogger('vgmdl').info( f'downloading track {track.id} as {file_path}')
            track.status = 'download started'
            db.session.commit()

            with urllib.request.urlopen(url) as phandle:
                with open(file_path, 'wb') as fh:
                    while True:
                        data = phandle.read(1024)
                        if not data:
                            logging.getLogger('vgmdl').error(
                                f"file {filename} download interrupted {downloaded_bytes}/{file_size} ({progress_percentage}%)")
                            break
                        fh.write(data)
                        downloaded_bytes += len(data)

                        # Calculate download progress as a percentage
                        progress_percentage = (
                            downloaded_bytes / file_size) * 100
                        logging.getLogger('vgmdl').debug(
                            f"file {filename} {downloaded_bytes}/{file_size} ({progress_percentage}%)")

            track.status = 'downloaded'
            track.filename = file_path
            track.filesize = file_size
            db.session.commit()
            pass
        except Exception as e:
            logging.getLogger('vgmdl').exception(
                f'error downloading track {track_task}')
            track.status = 'error'
            db.session.commit()
