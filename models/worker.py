import logging
from time import sleep
from models.storage import *
from sqlalchemy import or_
from vgmdl import VGMPageParser


def read_album(task):
    # album = Album.query.filter_by(id=task.reference).first()
    album = Album.query.get(task.reference)

    parser = VGMPageParser(album.url)

    #update album title and status
    albun_title = parser.get_albun_title()
    album.name = albun_title
    db.session.commit()

    if task.autostart:
        task.status = 'in progress'
        task.progress = 0
    db.session.commit()
    logging.getLogger('vgmdl').debug(f'album updated: {vars(album)}')
    logging.getLogger('vgmdl').debug(f'task updated: {vars(task)}')
    
    track_urls = parser.get_links()
    add_tracks_tasks(task.id, track_urls)

def add_tracks_tasks(album_task_id, track_urls):
    album_task = Task.query.get(album_task_id)
    album = Album.query.get(album_task.reference)
    # album_task = Task.query.filter_by(id=album_task_id).first()
    # album = Album.query.filter_by(id=album_task.reference).first()

    for track_url in track_urls:
        if track_url.endswith(album.format) or album.format == 'all':
            queueTrack(track_url, album_task_id)

def download_track(task):
    pass

def worker(app):
    with app.app_context():
        logging.getLogger('vgmdl').debug(f'starting worker')
        while True:
            try:
                # Fetch pending tasks from the database
                # pending_album_tasks = Task.query.filter( or_(Task.status=='pending', Task.status=='auto'), Task.type=='album').limit(10).all()
                pending_tasks = Task.query.filter_by( status='pending').limit(10).all()
                logging.getLogger('vgmdl').debug(f'pending_tasks: {len(pending_tasks)}')
                # Process each task
                for task in pending_tasks:
                    logging.getLogger('vgmdl').debug(f'processing task: {task.id} ({task.type})')
                    if task.type == 'album':
                        read_album(task)
                    if task.type == 'track':
                        download_track(task)
            except Exception as e:  
                logging.getLogger('vgmdl').exception(f'error processing pending tasks')

            # Sleep for a while before checking for new tasks again
            sleep(3)

