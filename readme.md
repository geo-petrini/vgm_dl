

# *main.py*
original file, works

eg: 
python main.py https://downloads.khinsider.com/game-soundtracks/album/mass-effect-expanded-soundtrack


# *run.py*
new version, also works
uses vgmdl.py as downloader and parser, by default fully threaded with 4 workers

eg: 
pyton run.py https://downloads.khinsider.com/game-soundtracks/album/mass-effect-expanded-soundtrack

# *gui.py*
work in progress for giving a console based ui to the tool
would like to integrate downloader.py from the rich examples

# *vgmdllib.py*
new version of vgmdl, with better queue management and possibility to interrupt the downloads queue
used by run.py and gui.py

# * app.py *
flask ui
uses icons from iconify.desing
https://icon-sets.iconify.design/

# TODO
- add small text file with original URL
- download album picture
    ```html
    <div class="albumImage">
        <a href="https://vgmsite.com/soundtracks/mass-effect-expanded-soundtrack/coverart.jpg" target="_blank">
            <img src="https://vgmsite.com/soundtracks/mass-effect-expanded-soundtrack/thumbs/coverart.jpg">
        </a><br>
    </div>
    ```
- implement a task queue
  - option 1: use a db with flask-sqlalchemy
    - define SQLALCHEMY_DATABASE_URI
    - define models
    - setup db: 
      - `flask db init`
      - `flask db migrate -m "Initial migration"`
      - `flask db upgrade` (repeat this every time changes are done)
      - db (sqlite) is in `./instance/storage.sqlite`
  - option 2: use redis as queue for flask tasks
    - deploy redis as docker container, standard port 6379
    - implement queue eg: https://realpython.com/flask-by-example-implementing-a-redis-task-queue/