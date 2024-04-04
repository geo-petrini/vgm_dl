from threading import Thread
from flask import Blueprint
from models.worker import worker

bp = Blueprint('worker', __name__)

def start_worker(app):
    worker_thread = Thread(target=worker, daemon=True, args=(app,))
    worker_thread.start()