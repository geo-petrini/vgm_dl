import logging
from flask import Blueprint, current_app, g, url_for, redirect, render_template, request, send_from_directory, abort
# from models.storage import queueAlbum
from models.storage import *
import json


bp = Blueprint('default', __name__)

@bp.route('/')
def home():
    return redirect(url_for('default.index'))

@bp.route('/index')
def index():
    content = ''
    return render_template("index.html", data=content, title='Video Game Music Downloader')

@bp.route('/status', methods=['GET'])
def get_status():
    pass 

@bp.route('/css/<theme>/<path:filename>')  # the "theme" folder does not exist but is there for routing and masking purpose
def serve_theme_css(theme, filename):
    if theme == 'bootstrap':
        return send_from_directory('static/css', f'bootstrap.min.css')
    else:
        return send_from_directory('static/css', f'bootstrap-{theme}.min.css')
    

@bp.route('/render_track/<track_id>', methods=['GET'])
def render_track(track_id):
    track = Track.query.filter(Track.id == track_id).first()
    return render_template("track.html", data=track)
