from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import make_response, render_template, jsonify
from flask_limiter import Limiter, RequestLimit
import http


limiter: Limiter | None = None


def limiter_register(app):
    global limiter

    def ratelimit_handler(request_limit: RequestLimit):
        return make_response(
            jsonify(error=f"ratelimit exceeded "),
            http.HTTPStatus.TOO_MANY_REQUESTS
        )

    # def default_error_responder(request_limit: RequestLimit):
    #     return make_response(
    #         jsonify(error=f"ratelimit exceeded {e.description}")
    #         render_template("my_ratelimit_template.tmpl", request_limit=request_limit),
    #
    #     )

    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["10/hour"],
    )
    limiter.init_app(app)
