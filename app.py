#!/bin/python3

'''
flask ui for vgmdl
'''

import logging
from flask import Flask
from flask import render_template
from flask_migrate import Migrate
import models.logmanager as logmanager
from models.storage import db




def create_app():
    app = Flask(__name__)
    logmanager.get_configured_logger(name='vgmdl', outpath="log")
    # app.logger.setLevel(logging.DEBUG)
    # socketio = SocketIO(app)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///storage.sqlite'
    app.config['SECRET_KEY'] = "dfsohjig894590uwfjl290"
    
    db.init_app(app)
    migrate = Migrate(app, db)

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