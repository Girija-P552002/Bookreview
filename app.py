import os
import sqlite3
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
import requests
import csv

app = Flask(__name__)
@app.route('/')
def index(): 
    return render_template('register.html')

@app.route("/register",methods=["GET","POST"])
def register():
    con=sqlite3.connect('database.db')
    c=con.cursor()
    if request.method=="POST":
        name = request.form["name"]
        mail = request.form["mail"]
        password = request.form["password"]   
        c.execute("CREATE TABLE IF NOT EXISTS accounts (name TEXT, mail TEXT, password TEXT)")

        result = c.execute("INSERT INTO accounts(name, mail, password) VALUES (:n, :m, :p)",
                    {"n": name, "m": mail, "p": password})
        con.commit() 
        return render_template("dashboard.html",message='succesfully signed up') 
    return render_template("register.html",message=None)   


@app.route("/logout")
def logout():
    return redirect(url_for('register'))       


@app.route("/login",methods=["POST","GET"])
def login():
    con = sqlite3.connect('database.db')
    c = con.cursor()
    if request.method =="POST":
        mail = request.form["mail"]
        password = request.form["password"] 
        result=c.execute("SELECT * FROM accounts Where mail = :m and password = :p",{"m":mail,"p":password}).fetchone() 
        
        if result is not None:
            if os.path.exists('log.txt'):
               os.remove('log.txt')
            f=open('log.txt','w')
            f.write(str(mail)) 
            f.close()

            return redirect(url_for('dashboard'))   

        message="mail or password is incorrect."    
        return render_template("login.html", message=message)
    return render_template("login.html",message = None)   

@app.route("/dashboard") 
def dashboard():
    return render_template("dashboard.html")

@app.route("/dashboard/search", methods=["POST"])
def search():
    if request.method =='POST':
     message = None
     con = sqlite3.connect('database.db')
     c = con.cursor()
     query1 = request.form["searchbox"]

     query ='%'+ query1.lower()+'%'
     # results = c.execute("SELECT * from books WHERE lower(title) LIKE :q OR isbn LIKE :q OR lower(author) LIKE :q",{"q":query}).fetchall()
     results = c.execute("SELECT * FROM books WHERE lower(title) LIKE :q OR isbn LIKE :q OR lower(author) LIKE :q", {"q": query}).fetchall()
    #  print(results)
     if query1:
        return render_template("search.html", results=results)
     else:
        return render_template("search.html", results=results[1:])
    return render_template("dashboard.html") 


@app.route("/info/<string:isbn>", methods=["GET", "POST"])
def info(isbn):
    con = sqlite3.connect('database.db')
    c = con.cursor()
    if request.method == "POST":
        comment = request.form["comment"]
        my_rating = request.form["stars"]
        f = open('log.txt', 'r')
        name=f.read()
        f.close()
        c.execute("""create table if not exists review(book_id, comment, rating)""")
        book = c.execute("INSERT INTO review (name, book_id, comment, rating) VALUES (:u, :b, :c, :r)", {"u":name , "b": isbn, "c": comment, "r": my_rating})
        con.commit()

    book = c.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    reviews = c.execute("SELECT * FROM review WHERE book_id = :q1", {"q1": isbn}).fetchall()

    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1O7xiWC9D6p2JmdhgX4LTw", "isbns": isbn})
    data = response.json()
    gr_rating = (data['books'][0]['average_rating'])

    return render_template("info.html", book_info=book, reviews=reviews, rating=gr_rating)

@app.route("/api/<string:isbn>")
def api(isbn):
    con = sqlite3.connect('database.db')
    c = con.cursor()
    book = c.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404
    
    c.execute("""create table if not exists review(name, book_id, comment, rating)""")
    book = c.execute("SELECT * FROM books WHERE isbn = :q", {"q": isbn}).fetchone()
    reviews = c.execute("SELECT * FROM review WHERE book_id = :q1", {"q1": isbn}).fetchall()

    response = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "1O7xiWC9D6p2JmdhgX4LTw", "isbns": isbn})
    data = response.json()
    gr_rating = (data['books'][0]['average_rating'])

    return render_template("info.html", book_info=book,reviews=reviews, rating=gr_rating)

if __name__ == "__main__":
    app.run(debug=True)