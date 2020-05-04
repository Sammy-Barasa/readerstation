import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy import create_engine
from sqlalchemy import Column, String, Integer, ForeignKey,Boolean, UniqueConstraint, PrimaryKeyConstraint,ext, Unicode,ForeignKeyConstraint, DateTime, func
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from werkzeug.security import generate_password_hash


# = SQLAlchemy(app=create_app())
engine = create_engine(os.getenv("DATABASE_URL"))
db= scoped_session(sessionmaker(bind=engine))
base = declarative_base()

class Book(base):
    __tablename__ = 'books'
    # __table_args__ = (
    #     PrimaryKeyConstraint('id'),
    #     UniqueConstraint(['isbn'], ['reviews.bookisbn'])
    #  
    #     )
    id=Column(Integer,primary_key=True,unique=True)
    isbn=Column(Unicode,nullable=False,unique=True)
    author=Column(String,nullable=False)
    year=Column(Integer,nullable=False)
    
    



class User(UserMixin,base):
    
    __tablename__ = 'users'
    id=Column(Integer,primary_key=True)
    name=Column(String(20),nullable=False)
    email=Column(String,nullable=False)
    password=Column(String,nullable=False)
    image_file = Column(String(20),nullable=False, default='default.png')
    # is_active = Column(Boolean(), default=True)
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.get_id=self.id
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
    
    def __str__(self):
        return f'{self.name}-{self.email}'

class Review(base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    rating = Column(Integer, nullable = True)
    comment = Column(String, nullable = True)
    owner=Column(Integer,nullable=False)
    bkid=Column(Integer,nullable=False)
    datereviewed= Column(DateTime, default=func.now())


    def __str__(self):
        return f'{self.owner}-{self.rating}-{self.datereviewed}'
base.metadata.create_all(engine)