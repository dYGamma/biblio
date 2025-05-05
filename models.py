from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from database import Base
import enum
from datetime import datetime
import bcrypt

class RoleEnum(enum.Enum):
    student   = 'student'
    librarian = 'librarian'
    admin     = 'admin'

class StatusEnum(enum.Enum):
    pending   = 'pending'
    confirmed = 'confirmed'
    cancelled = 'cancelled'
    issued    = 'issued'
    overdue   = 'overdue'
    returned  = 'returned'

class User(Base):
    __tablename__ = 'users'
    id            = Column(String, primary_key=True, index=True)
    name          = Column(String, nullable=False)
    role          = Column(Enum(RoleEnum), nullable=False)
    clazz         = Column(String, nullable=True)
    contact       = Column(String, nullable=True)
    password_hash = Column(String, nullable=False)
    orders        = relationship("Order", back_populates="user")

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.password_hash.encode())

class Book(Base):
    __tablename__ = 'books'
    id          = Column(Integer, primary_key=True, index=True)
    isbn        = Column(String, unique=True, nullable=True, index=True)
    title       = Column(String, nullable=False)
    author      = Column(String, nullable=False)
    genre       = Column(String, nullable=True)
    year        = Column(Integer, nullable=True)
    copies      = Column(Integer, default=1)
    description = Column(Text, nullable=True)
    added_at    = Column(DateTime, default=datetime.utcnow)
    orders      = relationship("Order", back_populates="book")

class Order(Base):
    __tablename__ = 'orders'
    id           = Column(Integer, primary_key=True, index=True)
    user_id      = Column(String, ForeignKey('users.id'), nullable=False)
    book_id      = Column(Integer, ForeignKey('books.id'), nullable=False)
    status       = Column(Enum(StatusEnum), default=StatusEnum.pending)
    request_date = Column(DateTime, default=datetime.utcnow)
    confirm_date = Column(DateTime, nullable=True)
    issue_date   = Column(DateTime, nullable=True)
    return_date  = Column(DateTime, nullable=True)
    due_date     = Column(DateTime, nullable=True)
    user         = relationship("User", back_populates="orders")
    book         = relationship("Book", back_populates="orders")
