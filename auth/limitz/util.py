from flask import request


def get_remote_address() -> str:
    return request.remote_addr or '127.0.0.1'
