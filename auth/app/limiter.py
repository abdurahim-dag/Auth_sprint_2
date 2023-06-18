from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


limiter: Limiter | None = None


def limiter_register(app):
    global limiter

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["20/second"],
    )
    limiter.init_app(app)
