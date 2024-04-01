#!/bin/python3

'''
flask ui for vgmdl
'''

from flask import Flask, flash, request, redirect, url_for, send_from_directory
from flask import render_template

app = Flask(__name__)

# socketio = SocketIO(app)

@app.route('/')
def home():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    content = ''
    return render_template("index.html", data=content, title='Video Game Music Downloader')

@app.route('/processurl', methods=['POST'])
def processUrl():
    if 'url' in request:
        pass

@app.route('/status', methods=['GET'])
def get_status():
    pass    

@app.route('/css/<theme>/<path:filename>')  # the "theme" folder does not exist but is there for routing and masking purpose
def serve_theme_css(theme, filename):
    if theme == 'bootstrap':
        return send_from_directory('static/css', f'bootstrap.min.css')
    else:
        return send_from_directory('static/css', f'bootstrap-{theme}.min.css')

if __name__ == "__main__":
    app.run("0.0.0.0", debug = True)
    # socketio.run(app, debug=True)