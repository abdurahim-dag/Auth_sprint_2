from functools import wraps
from typing import Callable
from typing import List

from fastapi import Cookie
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer

from .auth_handler import decodeJWT


class AuthRoles:
    def __init__(self, roles: List[str], auto_error: bool = True):
        self.auto_error = auto_error
        self.payload = None
        self.roles = roles

    async def __call__(self, request: Request):

        token = request.cookies.get("access_token_cookie")

        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=HTTP_403_FORBIDDEN, detail="Not authenticated"
                )
            else:
                return None

        if not self.verify_jwt(token):
            if self.auto_error:
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            else:
                return None

        return self.check_roles()

    def verify_jwt(self, jwtoken: str) -> bool:
        isTokenValid: bool = False

        try:
            payload = decodeJWT(jwtoken)
        except:
            payload = None

        if payload:
            isTokenValid = True
            self.payload = payload

        return isTokenValid

    def check_roles(self) -> bool:
        checked = False
        if self.roles:
            allowed = set(self.roles)

            passed = self.payload['roles']

            if set(passed) & allowed:
                checked = True

        return checked


def auth(roles: List[str]):
    return AuthRoles(roles, auto_error=False)
