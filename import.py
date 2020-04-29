import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#postgres://ibzqomiwufwmmj:5e882db3d5f8345d3a5149239811a41fccf32fd5c66acbeec9f36639ec969ded@ec2-184-72-236-3.compute-1.amazonaws.com:5432/dap5onkaiojh12
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    for isbn,title, author, year in reader:
        for isbn, title, author, year in reader:
            db.execute("INSERT INTO books (isbn,title,author,year) VALUES (:isbn , :title, :author, :year)",
                        {'isbn':isbn , 'title':title , 'author':author, 'year':year})
            print(f"Added {isbn}, {title} by {author} in {year}")
            db.commit()
        db.execute("INSERT INTO books (isbn,title, author, year) VALUES ( :isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author,  "year": year})
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                    {"isbn": isbn,"title": title,"author": author, "year": year})
        print(f"Added {title} of {isbn} by author {author}, {year} published.")
        db.commit()
if __name__ == "__main__":
    main()
