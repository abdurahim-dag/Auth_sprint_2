from typing import Callable
import dataclasses

@dataclasses.dataclass
class Settings:
    STORAGE_URI: str | None
    KEY_FUNC: Callable[[], str]
    DEFAULT: str = '20/second'
    KEY_PREFIX: str = 'RATELIMIT_'
