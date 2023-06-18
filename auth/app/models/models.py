import datetime
import hashlib
import os
from typing import List

from sqlalchemy import Boolean
from sqlalchemy import Column
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import UniqueConstraint
from sqlalchemy import event
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import validates
from sqlalchemy.sql import func

from .messages import Messages


class Base(DeclarativeBase):
    pass


class UserRole(Base):
    __tablename__ = "user_role"

    user_id = Column(ForeignKey("user.id", ondelete="CASCADE"), primary_key=True)
    role_id = Column(ForeignKey("role.id", ondelete="CASCADE"), primary_key=True)


class User(Base):
    __tablename__ = "user"
    # У пользователей обязательно уникальные nickname и email.
    __table_args__ = (
        UniqueConstraint("email"),
        UniqueConstraint("nickname"),
    )
    # Используемы алгоритм и количество итреаций при создании хэша пароля.
    _hash_name = 'sha256'
    _iterations = 100

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(1000))
    status: Mapped[bool] = mapped_column(Boolean(), default=False)
    password: Mapped[str] = mapped_column(String())

    roles: Mapped[List["Role"]] = relationship(
        secondary="user_role", back_populates="users"
    )
    user_social: Mapped["UserSocial"] = relationship(
        back_populates="user",
        cascade="all, delete",
        passive_deletes=True,
    )


    def __repr__(self) -> str:
      return f"User(id={self.id!r}, nickname={self.nickname!r})"

    def set_password(self, password: str):
        # Проверим пароль на длину.
        from app.config import settings
        if len(password) < settings.PASSWORD_LENGTH:
            raise ValueError(Messages.password_min_length)

        salt = os.urandom(32)
        hashed = hashlib.pbkdf2_hmac(self._hash_name, password.encode('utf-8'), salt, self._iterations)
        self.password = '%s$%s$%s$%d' % (self._hash_name, salt.hex(), hashed.hex(), self._iterations)

    def check_password(self, password):
        hash_name, salt, hashed, iter = self.password.split('$')
        hashed_plain_password = hashlib.pbkdf2_hmac(
            hash_name, password.encode('utf-8'), bytes.fromhex(salt), int(iter))
        if hashed_plain_password.hex() == hashed:
            return True
        else:
            return False

    @validates("email")
    def validate_email(self, key, email):
        if '@' not in email:
            raise ValueError(Messages.email_incorrect)
        return email


# Отправка сигнала на отправку email с требованием подтверждения почты.
@event.listens_for(User, 'after_insert')
def receive_after_insert(mapper, connection, target):
    from app.signals import user_created
    user_created.send(target)


class AccountHistory(Base):
    __tablename__ = "accounting"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer())
    type: Mapped[str] = mapped_column(String(30))
    ts: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    params: Mapped[str] = mapped_column(String())


class Role(Base):
    __tablename__ = "role"
    # У ролей уникальные имена.
    __table_args__ = (
        UniqueConstraint("name"),
    )

    id = Column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    users: Mapped[List[User]] = relationship(
        secondary="user_role", back_populates="roles"
    )

class UserSocial(Base):
    __tablename__ = "user_social"

    id: Mapped[str] = mapped_column(String(300), primary_key=True)
    login: Mapped[str] = mapped_column(String(300))
    email: Mapped[str] = mapped_column(String(1000))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

    user: Mapped["User"] = relationship(
        back_populates="user_social"
    )
