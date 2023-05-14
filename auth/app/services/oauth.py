from authlib.integrations.flask_client import OAuth


oauth: OAuth | None = None

def init_oauth(app):
    global oauth
    oauth = OAuth(app)
    oauth.register('yandex')
