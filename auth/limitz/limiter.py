import dataclasses

import flask
from config import Settings
from typing import Callable
from typing import Dict

# class HelloExtension:
#     def __init__(self, app=None):
#         if app is not None:
#             self.init_app(app)
#
#     def init_app(self, app):
#         app.before_request(...)

class Limiter:

    def __init__(
        self,
        key_func: Callable[[], str],
        *,
        app=None,
        storage_uri: str | None,
        default: str | None
    ):
        self._config = Settings(
            KEY_FUNC=key_func,
            STORAGE_URI=storage_uri
        )
        if default:
            self._config.DEFAULT = default

        self._endpoints: Dict[str, str] = {}

        if app:
            self.init_app(app)

    def init_app(self, app: flask.Flask) -> None:
        config = app.config

        for key in config.keys():
            if key.startswith(self._config.KEY_PREFIX):
                setattr(self._config, key, config[key])

        app.before_request(self._check_request_limit)
        app.after_request(self._inject_headers)



    def _add_endpoint(self, endpoint: str, limit: str):

    def _has_endpoint(self, endpoint: str) -> bool:

    def _resolve_limits():
        pass

    def _inject_headers(self):
        pass

    def limit(
            self,
            limit_value: str
            *,
            key_func: Optional[Callable[[], str]] = None,
    ) -> LimitDecorator:

    @property
    def storage(self) -> Storage:
        """
        The backend storage configured for the rate limiter
        """
        assert self._storage
        return self._storage


    def _check_request_limit(self) -> None:
        endpoint = flask.request.endpoint

        if failed_limits:
            raise RateLimitExceeded(
                sorted(failed_limits, key=lambda x: x[0].limit)[0][0],
                response=on_breach_response,
            )
