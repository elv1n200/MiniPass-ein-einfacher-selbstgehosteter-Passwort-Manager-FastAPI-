from sqlalchemy import Column, Integer, String, LargeBinary, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

    entries = relationship("PasswordEntry", back_populates="owner")


class PasswordEntry(Base):
    __tablename__ = "passwords"

    id = Column(Integer, primary_key=True, index=True)
    site = Column(String, index=True)
    username = Column(String)
    password = Column(LargeBinary)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="entries")
