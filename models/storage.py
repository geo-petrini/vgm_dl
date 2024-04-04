from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import UUIDType
from sqlalchemy import ForeignKey
from urllib.parse import unquote
import uuid
import logging

db = SQLAlchemy()


class Album(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String(255))
    name = db.Column(db.String(255))  # album name, track name
    format = db.Column(db.String(255))
    thumbnail = db.Column(db.Boolean)


class Track(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String(255))
    name = db.Column(db.String(255))  # album name, track name
    album_id = db.Column(UUIDType(), ForeignKey('album.id'))


class Task(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    type = db.Column(db.String(50))  # album, track
    reference = db.Column(UUIDType())  # album or track id
    progress = db.Column(db.Integer)
    autostart = db.Column(db.Boolean)
    status = db.Column(db.String(50), default='pending')


def queueAlbum(url, format, thumbnail, autostart):
    album = Album(
        url=url,
        format=format,
        thumbnail=thumbnail)
    db.session.add(album)
    db.session.commit()

    album_task = Task(
        type='album',
        reference=album.id,
        autostart=autostart,
        status='pending')
    db.session.add(album_task)
    db.session.commit()
    logging.getLogger('vgmdl').info(
        f'album task added: {album_task.id} reference {album_task.reference}')
    return album_task


def queueTrack(track_url, album_task_id):
    album_task = Task.query.filter_by(id=album_task_id).first()
    album = Album.query.filter_by(id=album_task.reference).first()

    track = Track(
        url=track_url,
        name=unquote(track_url.split('/')[-1]),
        album_id=album.id
    )
    db.session.add(track)
    db.session.commit()

    track_task = Task(
        type='track',
        reference=track.id,
        progress=0,
        status='pending' if album_task.autostart else 'waiting',
    )
    db.session.add(track_task)
    db.session.commit()

    logging.getLogger('vgmdl').info(
        f'track task added {track_task.id} reference {track_task.reference}')
    return track_task
