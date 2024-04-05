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
    title = db.Column(db.String(255))
    format = db.Column(db.String(255))
    thumbnail = db.Column(db.Boolean)
    status = db.Column(db.String(255)) 


class Track(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String(255))
    title = db.Column(db.String(255)) 
    album_id = db.Column(UUIDType(), ForeignKey('album.id'))
    filename = db.Column(db.String(255))
    filesize = db.Column(db.Integer())
    status = db.Column(db.String(255)) 
