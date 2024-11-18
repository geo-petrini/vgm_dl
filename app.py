#!/bin/python3

'''
flask ui for vgmdl
'''

from flask import Flask
from flask import render_template
# from flask_migrate import Migrate
from dotenv import load_dotenv

import models.logmanager as logmanager
from models.storage import db
# from models.redismanager import RedisManager

import os


def create_app():
    app = Flask(__name__)
    logmanager.get_configured_logger(name='vgmdl', outpath="log")

    load_dotenv(override=True)
    # socketio = SocketIO(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI', 'sqlite:///storage.sqlite')
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "dfsohjig894590uwfjl290")

    app.config['DOWNLOAD_FOLDER'] = os.environ.get('DOWNLOAD_FOLDER', "downloads") 
    app.config['DOWNLOAD_CHUNK_SIZE'] = os.environ.get('DOWNLOAD_CHUNK_SIZE', 1024*10)

    app.config['CACHE_REDIS_URL'] = os.environ.get('CACHE_REDIS_URL', "redis://localhost:6379/0")

    # redis_manager = RedisManager(app)
    
    db.init_app(app)
    # migrate = Migrate(app, db)

    from routes.default import bp as bp_routes
    app.register_blueprint(bp_routes)    

    from models.worker_manager import bp as bp_worker
    app.register_blueprint(bp_worker)      

    from models.worker_manager import start_worker
    start_worker(app)

    with app.app_context():
        db.create_all() #warning, this function creates tables but does not update them

    return app


if __name__ == "__main__":
    create_app().run(host = "0.0.0.0", debug=True)