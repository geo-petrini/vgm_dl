import redis
import re
import logging

class RedisManager:
    def __init__(self, app=None):
        self.app = app
        self.redis = None

        if app is not None:
            self.init_app(app)
            # self.redis_url_parser()

    def init_app(self, app):
        self.app = app
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['redis_manager'] = self

    # def redis_url_parser(self):
    #     pattern = r'redis://(?P<credentials>.*@)?(?P<host>[\w\.]+):(?P<port>\d+)/(?P<db>.*)'
    #     m = re.search(pattern, self.app.config['REDIS_URL'])
    #     out = {'host':None, 'port':None, 'db':None}
    #     if m:
    #         self.host = m.group('host')
    #         self.port = m.group('port')
    #         self.db = m.group('db')
    #         self.credentials = m.group('credentials').strip('@') if m.group('credentials') else None
        

    def get_redis(self):
        if self.redis is None:
            # self.redis = redis.Redis(host=self.host,
            #                    port=self.port,
            #                    db=self.db)
            try:
                self.redis = redis.from_url( self.app.config['REDIS_URL'] )
            except Exception as e:
                logging.getLogger('vgmdl').exception(f'error loading REDIS_URL variable {self.app.config["REDIS_URL"]}')

        return self.redis