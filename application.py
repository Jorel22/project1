#Author: Jordan Montenegro
import os
import requests
import json

from flask import Flask, session,render_template,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
#isben="038079527"# 

@app.route("/")
def index():
	#return "Project 1: TOD"
	#print( "hola")	
	
	#signin()
	return render_template("raiz1.html")
	
@app.route("/signin",methods=["GET", "POST"])
def signin():
	return render_template("signin.html")
	



@app.route("/login",methods=["GET","POST"])
def login():
	#if session["user"]=="none":
		#return "bad guy"
	session["user"] = "pepe"
	return render_template("login.html")
	#session.clear()
	session["user"] = "pepe"
	#return index()
  
  
@app.route("/logout")
def logout():
	session.clear()
	#session["user"] = "none"
	return render_template("login.html")
	#return login()
#def search_book():
	
@app.route("/validate",methods=["POST"])
def validate():
	if request.method == "POST":
		if session["user"] is None:
			return render_template("login.html")
			#return login()
		user = request.form.get("user")
		password = request.form.get("password")
		try:
			real=db.execute("SELECT password FROM users WHERE name=:user" ,{"user":user}).fetchone()
			real_password=real[0]
		except:
			return render_template("error.html",message="USer not signed in")
		
		if real_password==password:
			session.clear()
			session["user"] = user
			try:
				return render_template("inside.html",user=session["user"])	
			except:
				return render_template("error.html",message="Please enter again")
		else:
			return render_template("error.html",messaje="Wrong password.")

	else:
			return render_template("error.html",mensaje="You are not allowed to enter.")
@app.route("/user_added",methods=["GET","POST"])
def add_user():
	user = request.form.get("user")
	password = request.form.get("password")
	confirm = request.form.get("confirm")		
	if password!=confirm:
		return render_template("error.html",mensaje="Password doest not match")
	try:
		db.execute("INSERT INTO users (name, password) VALUES (:name, :password)",{"name": user, "password": password})
		db.commit()
	except:
		return render_template("error.html",mensaje="username already taken")
	
	return login()

@app.route("/search_books",methods=["POST"])
def search_book():
	isben= request.form.get("book_name")
	#if session["user"] is None:
	#	return render_template("error.html",message="Please enter again")
		
	try:
		books = db.execute("SELECT isbn,tittle,author,year FROM book1 WHERE UPPER(isbn) like UPPER(:isben) or UPPER(tittle) like UPPER(:isben) or UPPER(author) like UPPER(:isben)" ,{"isben": "%"+isben+"%"}).fetchall()
	except:
		return render_template("error.html",message="Error 404")
	if books is None:
		return render_template("error.html",message="No such book")
	
	
	try:
		return render_template("books.html",books=books,user=session["user"])
	except:
		return render_template("error.html",message="Please enter again")
	#for libro in books:
	#	print(libro[0])
	#return str(libro[2])
	
@app.route("/api/<isbn>",)
def search_book_isbn(isbn):
	isbn=str(isbn)
	try:
		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jUVZ3N2LJpznGsnTA80ng", "isbns":isbn}) 
		h=res.json()
	except:
		return render_template("error.html",message="404 not founnd")
	
	libro = db.execute("SELECT * FROM book1 WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
	if libro is None:
		return render_template("error.html",mensaje="Error 404")
	x = {"title":libro.tittle,"author":libro.author ,"year":libro.year ,"isbn":isbn,"review_count":int((h['books'][0])['work_ratings_count']),"average_score":float((h['books'][0])['average_rating'])}
	return x
	
@app.route("/seebooks/<book_isbn>",methods=["POST","GET"])
def book(book_isbn):
	#isben= request.form.get("book_isbn")
	#isben=str(book_isbn)
	res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jUVZ3N2LJpznGsnTA80ng", "isbns": book_isbn}) 
	h=res.json()
	book = db.execute("SELECT * FROM book1 WHERE isbn = :isbn", {"isbn": book_isbn}).fetchone()
	#title=(h['books'][0])['title']
	work_ratings_count=int((h['books'][0])['work_ratings_count'])
	average_rating=float((h['books'][0])['average_rating'])
	
	comments = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": book_isbn}).fetchall()
	try:
		return render_template("book_data.html",book=book,work_ratings_count=work_ratings_count,average_rating=average_rating,comments=comments,user=session["user"])
	except:
		return render_template("error.html",message="Please enter again")
@app.route("/add_review/<book_isbn>",methods=["POST"])
def add_review(book_isbn):
	#book_isbn=str(book_isbn)
	comment_text= request.form.get("comment_text")
	grade= int(request.form.get("grade"))
	try:
		db.execute("INSERT INTO reviews VALUES (:isbn, :user, :grade, :comment)",{"isbn":book_isbn,"user": session["user"], "grade":grade,"comment":comment_text})
		db.commit()
	except:
		return render_template("error_inside.html",mensaje="You already have graded this book",book_isbn=book_isbn)
	return book(book_isbn)
	#return render_template("error.html",mensaje=comment_text+str(grade))
	
	
