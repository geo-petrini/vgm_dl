import logging
from time import sleep
from sqlalchemy import or_
from flask import current_app
from models.storage import *
from vgmdl import VGMPageParser
# import redis
from urllib.parse import unquote
import math
import urllib
import uuid
import json
import os
import re
import base64

def worker(app):
    with app.app_context():
        while True:
            album = get_new_album() #from storage
            if album: read_album(album)

            track = get_new_track() #from storage
            if track: download_track(track)

            # update all album states
            update_albums()
            sleep(1)

            #old code
            # Dequeue album task data from Redis list
            # json_album_task_data = rd.rpop('albums_task_queue')
            # json_album_task_data = qm.pop('albums_task_queue')
            # if json_album_task_data:
            #     album_task_data = json.loads(json_album_task_data)
            #     read_album(album_task_data)



            # Dequeue track task data from Redis list
            # json_track_task_data = rd.rpop('tracks_task_queue')
            # json_track_task_data = qm.pop('tracks_task_queue')
            # if json_track_task_data:
            #     track_task_data = json.loads(json_track_task_data)
            #     download_track(track_task_data)


def read_album(album):
    parser = VGMPageParser(album.url)

    img_url = parser.get_album_image_url()
    logging.getLogger('vgmdl').debug(f'album img url "{img_url}"')
    album_image = read_album_image( img_url )
    album.title = parser.get_albun_title()
    album.thumbnail = album_image
    db.session.commit()

    track_urls = parser.get_links()
    add_tracks_tasks(album, track_urls)

def DEPRECATED_read_album(task):
    if task['url'] == None or task['url'] == '':
        logging.getLogger('vgmdl').warning(f'invalid url "{task["url"]}" skipping task')

    parser = VGMPageParser(task['url'])

    img = parser.get_album_image_url()
    logging.getLogger('vgmdl').warning(f'album img url "{img}"')
    album_image = read_album_image( img )

    album = Album(
        id=uuid.uuid4(),
        url=task['url'],
        title=parser.get_albun_title(),
        format=task['format'],
        thumbnail = album_image
    )
    db.session.add(album)
    db.session.commit()

    track_urls = parser.get_links()
    add_tracks_tasks(album, track_urls)    

def read_album_image(img_url):
    base64_image = None
    try:
        img_data = download(img_url)
        base64_image = base64.b64encode(img_data).decode('utf-8')
    except Exception as e:
        logging.getLogger('vgmdl').exception(f'error downloading album image invalid "{img_url}"')
    return base64_image

def add_tracks_tasks(album, track_urls):
    for track_url in track_urls:
        if track_url.endswith(album.format) or album.format == 'all':
            try:
                # TODO check if the given track_url is not already present in the db and queued for download (ignore if error or downloaded)
                track = Track(
                    # id=uuid.uuid4().hex,
                    url=track_url,
                    title=unquote(track_url.split('/')[-1]),
                    album_id=album.id,
                    status=album.status
                )
                db.session.add(track)
                db.session.commit()

                logging.getLogger('vgmdl').debug(
                    f'saved track {track.id} for album {album.id}')

                # task_data = {'url': track_url, 'track': track.id.hex}
                # redis_manager = current_app.extensions['redis_manager']
                # rd = redis_manager.get_redis()        
                # rd.lpush('tracks_task_queue', json.dumps(task_data))
                # qm.set('tracks_task_queue', json.dumps(task_data))

                # logging.getLogger('vgmdl').debug(f'saved task {task_data}')
            except Exception as e:
                logging.getLogger('vgmdl').exception(
                    f'error processing album track {track_url}')

def clean_path(path):
    invalid_chars = ['\\',  '/',  ':', '*',  '?',  '"',  '<',  '>',  '|']
    for ic in invalid_chars:
        while ic in path:
            path = path.replace(ic, ' ')
    path = re.sub('\s+', ' ', path)
    # path = path.replace(' ', '_')
    return path

def create_folder(folder_path):
    path = ''
    # logging.getLogger('vgmdl').debug(f'splitting folder path: "{folder_path}" with separator "{os.sep}"')
    for d in folder_path.split(os.sep):
        if not d: continue  #handle empty substings due to // occurrences
        path += d + os.sep
        if not os.path.isdir(path):
            # logging.getLogger('vgmdl').debug(f'creating folder path: "{path}"')
            os.mkdir(path)

    logging.getLogger('vgmdl').debug(f'final folder path: "{path}"')
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return True
    else:
        return False

def create_album_folder_path(album_folder, file_format):
    folder_path = os.path.join(current_app.config['DOWNLOAD_FOLDER'],
                                   album_folder,
                                   file_format)
    folder_path = os.path.normpath(folder_path)

    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        return folder_path
    
    logging.getLogger('vgmdl').debug(f'creating album folder {folder_path}')
    '''
    for unknown reasons neither os.makedirs(os.path.dirname(folder_path), exist_ok=True) nor pathlib.Path(folder_path).parent.mkdir(parents=True, exist_ok=True) work
    folders are not created, sometimes only the first part of the path but never fully
    because of this I had to write my own function to create folder paths
    '''
    if create_folder(folder_path):
        return folder_path
    
    # in case everything goes wrong
    logging.getLogger('vgmdl').error(f'album folder not created: "{folder_path}"')
    return None

def _prepare_download_path(track, album):
    if not track or not album:
        logging.getLogger('vgmdl').error(
            f'invalid track {track.id} and album {album.id} combination')
        return None
    else:
        logging.getLogger('vgmdl').debug(
            f'loaded track {track.id} and album {album.id}')

    album_folder = clean_path(album.title)
    filename = clean_path(track.title)
    _, file_extension = os.path.splitext(filename)
    file_format = file_extension.replace('.', '')

    file_path = None
    folder_path = create_album_folder_path(album_folder, file_format)
    if folder_path != None:
        file_path = os.path.join(folder_path, filename)
        file_path = os.path.normpath(file_path)

    return file_path

# def download_track(track_task):
#     try:
#         track = Track.query.filter_by(id=uuid.UUID(track_task['track'])).first()
#         album = Album.query.get(track.album_id)
#     except Exception as e:
#         logging.getLogger('vgmdl').exception(
#             f'error loading correct track and album for task {track_task}')
#         return None

def download_track(track):
    try:
        album = Album.query.get(track.album_id)
        if album.status == DOWNLOAD_QUEUED:
            album.status = DOWNLOAD_STARTED
    except Exception as e:
        logging.getLogger('vgmdl').exception(f'error loading correct album for track {track}')
        return None
    file_path = _prepare_download_path(track, album)

    if file_path:
        try:
            url = track.url

            filename = os.path.basename(file_path)

            response = urllib.request.urlopen(url)
            file_size = int(response.headers['Content-Length'])
            downloaded_bytes = 0

            logging.getLogger('vgmdl').info(f'downloading track {track.id} as {file_path}')
            track.status = DOWNLOAD_STARTED
            track.filesize = file_size
            db.session.commit()

            with urllib.request.urlopen(url) as phandle:
                with open(file_path, 'wb') as fh:
                    while True:
                        data = phandle.read(
                            current_app.config['DOWNLOAD_CHUNK_SIZE'])
                        if not data:
                            logging.getLogger('vgmdl').error(f"file {filename} download interrupted {downloaded_bytes}/{file_size} ({progress_percentage}%)")
                            break
                        fh.write(data)
                        downloaded_bytes += len(data)

                        # Calculate download progress as a percentage
                        progress_percentage = (downloaded_bytes / file_size) * 100
                        if math.floor(progress_percentage) % 1 == 0:
                            track.download_percentage = {math.floor(progress_percentage)}
                            try:
                                db.session.commit()
                            except Exception as e:
                                logging.getLogger('vgmdl').exception(f'error saving record for track {track}')
                            # logging.getLogger('vgmdl').debug(f"file {filename} downloaded {downloaded_bytes}/{file_size} ({progress_percentage}%)")
                        
                        if downloaded_bytes == file_size:                           
                            logging.getLogger('vgmdl').info(f"file {filename} download completed {downloaded_bytes}/{file_size} ({progress_percentage}%)")
                            break

            track.status = DOWNLOAD_COMPLETED
            track.filename = file_path
            db.session.commit()
            pass
        except Exception as e:
            logging.getLogger('vgmdl').exception(f'error downloading track {track}')
            track.status = DOWNLOAD_ERROR
            db.session.commit()
            # TODO cleanup partial downloads

def download(url):
    raw_data = None
    with urllib.request.urlopen(url) as phandle:
        raw_data = phandle.read()
    
    return raw_data

def update_albums():
    # albums = Album.query.filter(or_(Album.status != DOWNLOAD_COMPLETED, Album.status == None, Album.status == 'NULL')).all()
    albums = Album.query.filter(or_(Album.status == DOWNLOAD_STARTED)).all()
    for album in albums:
        logging.getLogger('vgmdl').debug(f"album {album.id} status '{album.status}'")
        tracks = Track.query.filter(Track.album_id == album.id).all()
        tracks_count = len(tracks)
        tracks_downloaded = 0
        tracks_errors = 0
        tracks_processed = tracks_downloaded + tracks_errors
        progress_percentage = 0
        logging.getLogger('vgmdl').debug(f"album {album.id}, checking download status for {tracks_count} tracks")

        for track in tracks:
            if track.status == DOWNLOAD_COMPLETED:
                tracks_downloaded += 1

            if track.status == DOWNLOAD_ERROR:
                tracks_errors += 1   

        tracks_processed = tracks_downloaded + tracks_errors        
        
        if tracks_count > 0:
            progress_percentage = (tracks_processed / tracks_count) * 100
            album.download_percentage = {math.floor(progress_percentage)}
            db.session.commit()

            if tracks_processed == tracks_count:
                logging.getLogger('vgmdl').info(f"album {album.id} download completed: {tracks_count}/{tracks_downloaded} errors: {tracks_errors} ({progress_percentage}%)")
                album.status = DOWNLOAD_COMPLETED
                db.session.commit()
        