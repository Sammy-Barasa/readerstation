import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from application import db



class Book(db.Model):
    __tablename__ = 'books'
    id=db.Column(db.Integer,primary_key=True)
    isbn=db.Column(db.Integer,nullable=False)
    author=db.Column(db.String,nullable=False)
    year=db.Column(db.Integer,nullable=False)


class User(db.Model):
    __tablename__ = 'users'
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(20),nullable=False)
    email=db.Column(db.String,nullable=False)
    password=db.Column(db.String,nullable=False)
    image_file = db.Column(db.String(20),nullable=False, default='default.png')

    def __str__(self):
        return f'{self.name}-{self.email}'
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    person = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    book_isbn = db.Column(db.Integer, db.ForeignKey('Book.isbn'), nullable=False)
    rating = db.Column(db.Integer, nullable = True)
    comment = db.Column(db.String, nullable = True)

    def __str__(self):
        return f'{self.owner}-{self.rating}'
db.create_all()