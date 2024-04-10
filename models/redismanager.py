import redis
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