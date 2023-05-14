from dataclasses import dataclass
from gettext import gettext as _


@dataclass
class Messages:
    """Дата-класс текстовых описания ответов ручек."""
    signup_fields_exist: str = _('Nickname, email or password not sent')
    email_incorrect: str = _('Email is not correct!')
    password_min_length: str = _('Minimal length password is 8 symbols!')
    login_exist: str = _('Nickname or email already exists')
    server_error: str = _('Internal server error')
    subject: str = _('Welcome to Movie app!')
    message: str = _('Dear %s, Welcome to Movie app! Pleas confirm email! %s')
    token_not_found: str = _('Token with %s not found!')
    user_not_found: str = _('User not found!')
    user_email_confirmed: str = _('User email confirmed!')
    login_fail: str = _('Bad username or password!')
    forbidden: str = _('Forbidden access!')
