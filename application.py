import os
import csv
import json
import requests
from bs4 import BeautifulSoup 
from flask import Flask, session, redirect,render_template, request, jsonify, url_for
from flask_session import Session
from flask_login import LoginManager, login_user, current_user, logout_user, login_required
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import bcrypt
import datetime



app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")


# keys=secrets.token_urlsafe(16)
# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# app.config['SECRET_KEY'] ='qwsvxjghbnlkhssewfgttysvxbv'
# app.config['SQLALCHEMY_DATABASE_URI']=os.getenv("DATABASE_URL")
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
# Session(app)
Session(app)
# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return user.get(user_id)

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
        passwordToHash=password.encode('utf-8')
        harshed_password=bcrypt.hashpw(passwordToHash, bcrypt.gensalt())
        # get email
        email=request.form.get('email')
        # store in_database 
        image_file=""
        db.execute("INSERT INTO users(name,email, password, image_file) VALUES ( :name, :email, :password, :image_file)",
                   {"name": name, "email": email, "password": harshed_password, "image_file": image_file})
        db.commit()
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
        passwod=request.form.get('password')
        print(passwod)
        # verify username
        user=db.execute("SELECT * FROM users WHERE email LIKE :email LIMIT 1",{ "email": '%' + email + '%'}).fetchone()
        print(user.password)
        hashed_=user.password
        a=bcrypt.checkpw(hashed_,passwod.encode('utf-8')) != hashed_
        print(a)
        # verify password
        if bcrypt.hashpw(passwod.encode('utf-8'), bcrypt.gensalt()) != hashed_:
            return render_template("login.html")
        else:
            a=bcrypt.hashpw(passwod.encode('utf-8'), bcrypt.gensalt()) != hashed_
            print(a)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect("/")
        
       
@app.route("/searchpage" ,methods=["GET","POST"])
def bookpage():
    #through get,output all books from database 
    if request.method=="GET":
        result= db.execute("SELECT * FROM books")
        return render_template("user.html",result=result)
    else:
        # there is a seeach and we perfom it
        searchdata=request.form.get("search")
        search=searchdata.lower()
        print(search)
        try:
            results=db.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE :search) OR (LOWER(title) LIKE :search) OR (LOWER(author) LIKE :search) LIMIT 50",
            { "search": '%' + search + '%'} ).fetchall()
            print(results)
            num=len(results)
            return render_template("user.html",search_result=results,num=num)
        except Exception as identifier:
            print(identifier)
            return render_template("user.html")
@app.route("/book/<bn>")
@login_required
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
    bookinfom=db.execute("SELECT * FROM books WHERE (LOWER(isbn) LIKE :bn) LIMIT 1", {"bn":'%'+ sbn +'%'}).fetchall()
    print(bookinfom)
    # review of the book from our database
    revs=db.execute("SELECT * FROM reviews WHERE (LOWER(book_isbn) LIKE :bn)",{"bn":'%'+ sbn +'%'}).fetchall()
    print(revs)
    #output parameters of clicked book
    return render_template("book.html",b=b,urlimg=bookUrl,d=bookTitle,e=bookDescription,bookinfom=bookinfom,review=revs)
@app.route("/reviews/<book_isbn>", methods=["POST"])
@login_required
def bookReview(book_isbn):
    # get isbn of book
    book_isbn=book_isbn
    print(book_isbn)
    # get comment from form
    comment=request.form.get("review")
    print(comment)
    # get rating from form 
    rating=request.form.get("rating")
    print(rating)
    #owner
    #add to database
    # db.execute("INSERT INTO reviews(person,book_isbn,comments,rating) VALUES ( :person, :book_isbn, :comments, :rating)",{"person": person, "book_isbn": book_isbn, "comments": comment, "rating": rating})
    # db.commit()
    return redirect(url_for('book', bn=book_isbn))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/login")
