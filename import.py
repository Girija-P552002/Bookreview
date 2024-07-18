import csv
import sqlite3

con = sqlite3.connect('database.db')
c = con.cursor()
c.execute("""create table if not exists books(isbn TEXT, title TEXT, author TEXT, year TEXT)""")
f = open("books.csv")
reader = csv.reader(f)
header = next(reader)

print("Running script ... ")
for isbn, title, author, year in reader:
    c.execute("INSERT INTO books(isbn, title, author, year) VALUES(:i, :t, :a, :y)", {"i": isbn, "t": title, "a": author, "y": year})

con.commit()