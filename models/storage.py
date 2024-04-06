from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import UUIDType
from sqlalchemy import ForeignKey
from urllib.parse import unquote
import uuid
import json
import logging

db = SQLAlchemy()


class Album(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String(255))
    title = db.Column(db.String(255))
    format = db.Column(db.String(255))
    thumbnail = db.Column(db.String(90000))
    status = db.Column(db.String(255)) 

    def to_json(self):
        d = {
            'id' : self.id.hex,
            'url' : self.url,
            'title' : self.title,
            'format' : self.format,
            'status' : self.status,
            'thumbnail' : self.thumbnail
        }
        return json.dumps(d)


class Track(db.Model):
    id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    url = db.Column(db.String(255))
    title = db.Column(db.String(255)) 
    album_id = db.Column(UUIDType(), ForeignKey('album.id'))
    filename = db.Column(db.String(255))
    filesize = db.Column(db.Integer())
    status = db.Column(db.String(255)) 
    
    def to_json(self):
        d = {
            'id' : self.id.hex,
            'url' : self.url,
            'title' : self.title,
            'album_id' : self.album_id.hex,
            'filename' : self.filename,
            'filesize' : self.filesize,
            'status' : self.status
        }
        return json.dumps(d)    