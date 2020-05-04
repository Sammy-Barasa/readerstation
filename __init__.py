# import os
# from flask import Flask
# from flask_sqlalchemy import SQLAlchemy
# from flask_login import LoginManager
# from flask_session import Session
# from bs4 import BeautifulSoup 
# from flask import Flask, session, redirect,render_template, request, jsonify, url_for, flash
# from flask_login import LoginManager, login_user, current_user, logout_user, login_required 
# from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy import create_engine
# from sqlalchemy.orm import scoped_session, sessionmaker
# from flask_bcrypt import Bcrypt
# from .models import User
# import bcrypt
# import datetime




# app = Flask(__name__)
# # keys=secrets.token_urlsafe(16)
# # Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
# app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")

# # bcrypt = Bcrypt(app)
# Session(app)
# db=SQLAlchemy()
# db.init_app(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'