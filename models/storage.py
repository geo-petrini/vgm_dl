from urllib.parse import unquote
import uuid
import json
import logging
import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_utils import UUIDType
from sqlalchemy import ForeignKey, inspect
from sqlalchemy.sql import or_


db = SQLAlchemy()

# DOWNLOAD_PAUSED = 'download paused'
DOWNLOAD_QUEUED = 'download queued'
DOWNLOAD_STARTED = 'download started'
DOWNLOAD_COMPLETED = 'download completed'
DOWNLOAD_ERROR = 'download error'

def get_uuid():
    # return uuid.uuid4.hex
    return uuid.uuid4().hex

def to_uuid(id):
    return uuid.UUID(id).hex


class Album(db.Model):
    # id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    url = db.Column(db.String(255))
    title = db.Column(db.String(255))
    format = db.Column(db.String(255))
    thumbnail = db.Column(db.String(90000))
    status = db.Column(db.String(255), default=DOWNLOAD_QUEUED) 
    download_percentage = db.Column( db.Float() )
    ts_add = db.Column( db.Float(), default=datetime.datetime.now().timestamp() )
    ts_finish = db.Column( db.Float() )

    def to_json(self):
        d = {
            'id' : self.id,
            'url' : self.url,
            'title' : self.title,
            'format' : self.format,
            'status' : self.status,
            'thumbnail' : self.thumbnail,
            'download_percentage' : self.download_percentage
        }
        return json.dumps(d)
    
    def __repr__(self):
        return f'Album(title="{self.title}", url="{self.url}, status={self.status})'


class Track(db.Model):
    # id = db.Column(UUIDType(), primary_key=True, default=uuid.uuid4)
    id = db.Column(db.String(36), primary_key=True, default=get_uuid )
    url = db.Column(db.String(255))
    title = db.Column(db.String(255)) 
    # album_id = db.Column(UUIDType(), ForeignKey('album.id'))
    album_id = db.Column(db.String(16), ForeignKey('album.id'))
    filename = db.Column(db.String(255))
    filesize = db.Column(db.Integer())
    status = db.Column(db.String(255), default=DOWNLOAD_QUEUED)
    download_percentage = db.Column( db.Float() )
    ts_add = db.Column( db.Float(), default=datetime.datetime.now().timestamp() )
    ts_finish = db.Column( db.Float() )
    
    def to_json(self):
        d = {
            'id' : self.id,
            'url' : self.url,
            'title' : self.title,
            'album_id' : self.album_id,
            'filename' : self.filename,
            'filesize' : self.filesize,
            'status' : self.status,
            'download_percentage' : self.download_percentage,
        }
        return json.dumps(d)    
    
    def __repr__(self):
        return f'Track(title="{self.title}", url="{self.url}, status={self.status})'    
    

def get_new_album():
    # return Album.query.filter_by(status=DOWNLOAD_QUEUED).first()
    # stmt = db.select(Album).filter( or_(Album.status==DOWNLOAD_QUEUED, Album.status==DOWNLOAD_PAUSED) )
    stmt = db.select(Album).filter( or_(Album.status==DOWNLOAD_QUEUED) )
    result = db.session.execute(stmt).scalars().first()
    # logging.getLogger('vgmdl').debug(f'result: {result}')
    return result

def get_new_track():
    return Track.query.filter_by(status=DOWNLOAD_QUEUED).first()

def tables_exist():
    for table_name in ['album', 'track']:
        # if not db.engine.dialect.has_table(db, table_name):
        if not inspect(db.engine).has_table(table_name):
            logging.getLogger('vgmdl').error(f'table "{table_name}" does not exist')
            return False
        
    return True
