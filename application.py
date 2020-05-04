import os
import csv
import json
import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_session import Session
from bs4 import BeautifulSoup 
from flask import Flask, session, redirect,render_template, request, jsonify, url_for, flash
from flask_login import LoginManager, login_user, current_user, logout_user, login_required 
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt
from .models import User
import bcrypt
import datetime




app = Flask(__name__)
# keys=secrets.token_urlsafe(16)
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")

# bcrypt = Bcrypt(app)
# Session(app)
db=SQLAlchemy()
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
# login_manager.session_protection = "strong"
# login_serializer = app.secret_key
@login_manager.user_loader
def load_user(user_id):
    try:
        return dtb.query(User).filter(User.id == int(user_id)).one()
    except:
        return None
    # return dtb.query(User).filter(User.id == int(user_id)).one()

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database

engine = create_engine(os.getenv("DATABASE_URL"))
dtb = scoped_session(sessionmaker(bind=engine))
@app.route("/")
def index():
    # show account
    # show reviews output
    # see other reviews
    return render_template("user.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method =="GET":
        return render_template("register.html")
    else:
        # get username 
        name=request.form.get('name')
        # get password
        password=request.form.get('password')
        # passwordToHash=password.encode('utf-8')
        hashed_password=generate_password_hash(password, method='sha256')
        # get email
        email=request.form.get('email')
        # store in_database 
        user=User(
            name=name,
            email=email,
            password=password
        )
        dtb.add(user)
        dtb.commit()
        print('added {},{}'.format(name,email))
        return render_template("login.html")
        
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="GET":
        return render_template("login.html")
    else:
        # get username
        email=request.form.get('email')
        # get password
        passwordToCheck=request.form.get('password')
        print(passwordToCheck)
        # verify username
        user=dtb.execute("SELECT * FROM users WHERE email LIKE :email LIMIT 1",{ "email": '%' + email + '%'}).fetchone()
        # verify user,bypassing veryfying password *I have not solved bycrypt problems
        checkpwhashed=check_password_hash(user.password, passwordToCheck)
        #get remember bool
        remember = True if request.form.get('remember') else False
        if not user and check_password_hash(user.password, passwordToCheck):
            return render_template("login.html")
        else:
            # load_user(user.id)
            # login_user(user,remember=remember,force=True)
            session['logged_in'] = True
            # session=True 
            # user.is_authenticated = True
            # print(user)
            # next_page = request.args.get('next')
            # print(next_page)
            return  redirect(url_for('index'))   
        
       
@app.route("/searchpage" ,methods=["GET","POST"])
def bookpage():
    #through get,output all books from database 
    if request.method=="GET":
        result= dtb.execute("SELECT * FROM books")
        return render_template("user.html",result=result)
    else:
        # there is a seeach and we perfom it
        searchdata=request.form.get("search")
        search=searchdata.lower()
        print(search)
        try:
            results=dtb.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE :search) OR (LOWER(title) LIKE :search) OR (LOWER(author) LIKE :search) LIMIT 50",
            { "search": '%' + search + '%'} ).fetchall()
            print(results)
            num=len(results)
            return render_template("user.html",search_result=results,num=num)
        except Exception as identifier:
            print(identifier)
            return render_template("user.html")
@app.route("/book/<bn>")
def book(bn):
    #get here after clicking a book,after submitting review
    #res=requests.get('https://www.goodreads.com/book/isbn/0441172717?user_id=110825791&format=json') (get book rating from googreads api)
    
    # show book from good reads api
    response=requests.get("https://www.goodreads.com/book/isbn/"+bn,params={"user_id":"110825791","format":"json"})
    c=response.json()['reviews_widget']
    # returns html page
    soup=BeautifulSoup(c,'lxml')
    bookTitle=soup.a.text
    datam=soup.a['href']
    page=requests.get(datam).text 
    # destructuring the page to obtain book title, book image url & book description
    book=BeautifulSoup(page,'lxml')
    bookUrl=book.find('img',id='coverImage')['src']
    bookDescription=book.find('div',id='descriptionContainer').text
    print(bookUrl)
    print(bookTitle)
    print(bookDescription)
    # get book rating from googreads api
    res = requests.get("https://www.goodreads.com/book/review_counts.json",params={"isbns":bn,"key":"NxHR0wNCivzIEefBextQ"})
    c=res.json()
    b=c['books'][0]
    print(b)
    sbn=bn.lower()
    bookinfom=dtb.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE :bn) LIMIT 1", {"bn":'%'+ sbn +'%'}).fetchall()
    print(bookinfom[0][0])
    # review of the book from our database
    revs=dtb.execute("SELECT * FROM reviews WHERE (bkid = :bn)",{"bn": bookinfom[0][0]}).fetchall()
    print(revs)
    #output parameters of clicked book
    return render_template("book.html",b=b,urlimg=bookUrl,d=bookTitle,e=bookDescription,bookinfom=bookinfom,review=revs)
@app.route("/reviews/<book_isbn>", methods=["POST"])
def bookReview(book_isbn):
    person=current_user.id
    # get isbn of book
    book_isbn=book_isbn
    print(book_isbn)
    # get book to retrieve its bkid
    book=dtb.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE :bn) LIMIT 1", {"bn":'%'+ book_isbn +'%'}).fetchall()
    # get comment from form
    comment=request.form.get("review")
    print(comment)
    # get rating from form 
    rating=request.form.get("rating")
    print(rating)
    #owner
    #add to database
    dtb.execute("INSERT INTO reviews(rating,comment,bkid) VALUES ( :rating, :comments, :bkid)",{"rating": rating, "comment": comment,  "bkid": book.id,})
    dtb.commit()
    return redirect(url_for('book', bn=book_isbn))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")

