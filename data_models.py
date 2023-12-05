from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Date)
    date_of_death = db.Column(db.Date)
    books = db.relationship('Book', backref='author', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Author(id={self.id}, name={self.name}, birth_date={self.birth_date}, date_of_death={self.date_of_death})>"

    def __str__(self):
        return f"Author: {self.name}, ID: {self.id}, Birth Date: {self.birth_date}, Date of Death: {self.date_of_death}"


class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)  # Add the new rating column

    def __repr__(self):
        return f"<Book(id={self.id}, isbn={self.isbn}, title={self.title}, publication_year={self.publication_year}, author_id={self.author_id})>"

    def __str__(self):
        return f"Book: {self.title}, ISBN: {self.isbn}, Year of Publication: {self.publication_year}, Author: {self.author.name}"

# Create the tables


db.create_all()
