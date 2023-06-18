import time
import jwt
from core.config import config


with open(config.auth_public_key_path) as f:
    JWT_SECRET = f.read()
JWT_ALGORITHM = config.auth_algorithm


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except:
        return {}