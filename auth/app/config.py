from pydantic import BaseSettings, Field
from datetime import timedelta


class Settings(BaseSettings):
    username: str = Field(..., env='AUTH_DB_USER')
    password: str = Field(..., env='AUTH_DB_PASSWORD')
    host: str = Field(..., env='AUTH_DB_HOST')
    port: str = Field(..., env='AUTH_DB_PORT')
    dbname: str = Field(..., env='AUTH_DB_NAME')

    email_sender: str = Field(..., env='AUTH_EMAIL_SENDER')
    email_password: str = Field(..., env='AUTH_EMAIL_PASSWORD')
    email_host: str = Field(..., env='AUTH_EMAIL_HOST')
    email_port: str = Field(..., env='AUTH_EMAIL_PORT')

    EMAIL_SENDER: str = Field(..., env='AUTH_EMAIL_SENDER')
    EMAIL_PASSWORD: str = Field(..., env='AUTH_EMAIL_PASSWORD')
    EMAIL_HOST: str = Field(..., env='AUTH_EMAIL_HOST')
    EMAIL_PORT: str = Field(..., env='AUTH_EMAIL_PORT')

    REDIS_HOST: str = Field(..., env='AUTH_REDIS_HOST')
    REDIS_PORT: int = Field(6379, env='AUTH_REDIS_PORT')
    REDIS_DB: int = Field(0, env='AUTH_REDIS_DB')

    JWT_COOKIE_HTTPONLY: bool = True

    JWT_TOKEN_LOCATION: list = ["cookies",]
    JWT_COOKIE_SECURE: bool = False
    JWT_SESSION_COOKIE: bool = False
    JWT_ALGORITHM: str = Field('RS256', env='AUTH_JWT_ALGORITHM')

    jwt_refresh_token_expires: int = Field(43200, env='AUTH_JWT_REFRESH_KEY_TTL')
    jwt_access_token_expires: int = Field(60, env='AUTH_JWT_ACCESS_KEY_TTL')
    jwt_private_key_path: str = Field('private.key', env='AUTH_JWT_PRIVATE_KEY_PATH')
    jwt_public_key_path: str = Field('public.key', env='AUTH_JWT_PUBLIC_KEY_PATH')

    APPLICATION_ROOT = '/auth'
    SECRET_KEY = 'mysecretkey'
    PASSWORD_LENGTH = 8

    YANDEX_CLIENT_ID: str = Field('e20cca1c8afc4604ba5b7d2132e45aa4', env='YANDEX_CLIENT_ID')
    YANDEX_CLIENT_SECRET: str  = Field('9b19c2852fd6433da7d0aad954757847', env='YANDEX_CLIENT_SECRET')
    YANDEX_ACCESS_TOKEN_URL: str  = Field('https://oauth.yandex.ru/token', env='YANDEX_ACCESS_TOKEN_URL')
    YANDEX_AUTHORIZE_URL: str  = Field('https://oauth.yandex.ru/authorize', env='YANDEX_AUTHORIZE_URL')
    YANDEX_API_BASE_URL: str  = Field('https://login.yandex.ru/info', env='YANDEX_API_BASE_URL')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.dbname}"

    @property
    def JWT_REFRESH_TOKEN_EXPIRES(self):
        return timedelta(minutes=self.jwt_refresh_token_expires)

    @property
    def JWT_PRIVATE_KEY(self):
        return open(self.jwt_private_key_path, 'rb').read()

    @property
    def JWT_PUBLIC_KEY(self):
        return open(self.jwt_public_key_path, 'rb').read()

    @property
    def JWT_ACCESS_TOKEN_EXPIRES(self):
        return timedelta(minutes=self.jwt_refresh_token_expires)

    @property
    def redis_conn_str(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    # Limiter
    RATELIMIT_STORAGE_URI = redis_conn_str
    RATELIMIT_STRATEGY = 'fixed-window'
    RATELIMIT_HEADERS_ENABLED = True


settings: Settings | None = None
