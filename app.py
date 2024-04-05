#!/bin/python3

'''
flask ui for vgmdl
'''

import logging
from flask import Flask
from flask import render_template
from flask_migrate import Migrate
import redis
# from flask_redis import FlaskRedis
import models.logmanager as logmanager
from models.storage import db
import re


class RedisManager:
    def __init__(self, app=None):
        self.app = app
        self.redis = None

        if app is not None:
            self.init_app(app)
            self.redis_url_parser()

    def init_app(self, app):
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['redis_manager'] = self

    def redis_url_parser(self):
        pattern = r'redis://(?P<host>\w+):(?P<port>\d+)/(?P<db>.*)'
        m = re.search(pattern, self.app.config['REDIS_URL'])
        out = {'host':None, 'port':None, 'db':None}
        if m:
            self.host = m.group('host')
            self.port = m.group('port')
            self.db = m.group('db')
        

    def get_redis(self):
        if self.redis is None:
            self.redis = redis.Redis(host=self.host,
                               port=self.port,
                               db=self.db)
        return self.redis


def create_app():
    app = Flask(__name__)
    logmanager.get_configured_logger(name='vgmdl', outpath="log")
    # app.logger.setLevel(logging.DEBUG)
    # socketio = SocketIO(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storage.sqlite'
    app.config['SECRET_KEY'] = "dfsohjig894590uwfjl290"
    app.config['REDIS_URL'] = "redis://rpi:6379/0"
    app.config['DOWNLOAD_FOLDER'] = r"C:\Users\geope\Localworks\python\vgm_dl\downloads"

    redis_manager = RedisManager(app)
    # redis = Redis(host='rpi', port=6379, db=0)
    # redis_client = FlaskRedis(app)
    
    db.init_app(app)
    # migrate = Migrate(app, db)

    from routes.default import bp as bp_routes
    app.register_blueprint(bp_routes)    

    from models.worker_manager import bp as bp_worker
    app.register_blueprint(bp_worker)      

    from models.worker_manager import start_worker
    start_worker(app)

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    # Initialize the Flask application context to work with the database
    # app.app_context().push()
    # Start the worker in a daemon thread
    # socketio.run(app, debug=True)
    # app.run("0.0.0.0", debug = True)
    # create_app().run(host = "0.0.0.0", debug=True, ssl_context='adhoc')
    create_app().run(host = "0.0.0.0", debug=True)