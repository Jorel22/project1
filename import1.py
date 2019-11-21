import csv
import os
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
	f = open("1.csv")
	reader = csv.reader(f)

	
	for isbn,title,author,year in (reader):
		if isbn =="isbn":
			continue
		res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "jUVZ3N2LJpznGsnTA80ng", "isbns": isbn})
		#print(f"This is the {res}")
		h=res.json()
		#print(h)
		#year=year
		h1=int((h['books'][0])['work_ratings_count'])
		h2=float((h['books'][0])['average_rating'])
		#print(f"isbn={isbn} title={tittle}  author={author}  year={year}")
		#print(f"title={tittle}")
		db.execute("INSERT INTO reviews (title,author,year,isbn,review_count,average_score) VALUES (:title, :author, :year,:isbn,:review_count,:average_score)",{"title": title, "author": author, "year": year,"isbn": isbn,"review_count":h1,"average_score":h2})
		print(f"Addedd {title},{h1}")
	db.commit()
 
if __name__ == "__main__":
	main()
