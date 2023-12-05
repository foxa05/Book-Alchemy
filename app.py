from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_
from data_models import db, Author, Book
import requests

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)


# Function to get redesigned UI from ChatGPT
def get_redesigned_ui(text):
    api_key = "E3gUwmAmy5bUlYZUJKs2T3BlbkFJLe00jmv6xlrl2edbbnPX"
    endpoint = "https://api.chatgpt.com/v1/chat"
    prompt = f"Redesign the UI of my digital library app:\n{text}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "messages": [{"role": "system", "content": "You are a helpful assistant."}],
        "max_tokens": 100,
        "temperature": 0.7,
        "n": 1,
        "stop": ["\n"],
        "prompt": prompt,
    }

    response = requests.post(endpoint, headers=headers, json=data)
    redesigned_text = response.json()["choices"][0]["message"]["content"]

    return redesigned_text


# Function to get book recommendation from ChatGPT
def get_recommendation_from_chatgpt(books_text):
    api_key = "E3gUwmAmy5bUlYZUJKs2T3BlbkFJLe00jmv6xlrl2edbbnPX"
    endpoint = "https://api.chatgpt.com/v1/chat"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    data = {
        "messages": [{"role": "system", "content": "You are a helpful assistant."}],
        "max_tokens": 100,
        "temperature": 0.7,
        "n": 1,
        "stop": ["\n"],
        "prompt": f"Recommend a book based on my reading history:\n{books_text}",
    }

    response = requests.post(endpoint, headers=headers, json=data)
    recommendation = response.json()["choices"][0]["message"]["content"]

    return recommendation


# Add authors
@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    if request.method == 'POST':
        name = request.form['name']
        birth_date = request.form['birth_date']
        date_of_death = request.form['date_of_death']

        new_author = Author(name=name, birth_date=birth_date, date_of_death=date_of_death)
        db.session.add(new_author)
        db.session.commit()

        return render_template('add_author.html', success_message="Author added successfully")

    return render_template('add_author.html')


# Add books
@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    authors = Author.query.all()

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
        db.session.add(new_book)
        db.session.commit()

        return render_template('add_book.html', authors=authors, success_message="Book added successfully")

    return render_template('add_book.html', authors=authors)


# Search books
@app.route('/search_books', methods=['GET'])
def search_books():
    search_query = request.args.get('search', '')

    # Use the `ilike` function for case-insensitive search on both title and author name
    search_result = Book.query.filter(or_(Book.title.ilike(f"%{search_query}%"), Book.author.has(Author.name.ilike(f"%{search_query}%")))).all()

    if not search_result:
        message = f"No books found for the search term '{search_query}'."
    else:
        message = f"Search results for '{search_query}':"

    return render_template('home.html', books=search_result, search_message=message)


# Delete book route
@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    try:
        # Get the book by ID
        book = Book.query.get(book_id)

        if not book:
            flash("Book not found.", 'error')
        else:
            # Delete the book
            db.session.delete(book)
            db.session.commit()

            flash("Book deleted successfully.", 'success')

            # Check if the author has no other books, delete the author
            author = Author.query.get(book.author_id)
            if author and not author.books:
                db.session.delete(author)
                db.session.commit()
                flash("Author deleted since no other books by this author.", 'info')

    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f"An error occurred: {str(e)}", 'error')

    return redirect(url_for('home'))


# UI Redesign route
@app.route('/ui_redesign', methods=['GET', 'POST'])
def ui_redesign():
    if request.method == 'POST':
        user_input = request.form['user_input']
        redesigned_ui = get_redesigned_ui(user_input)
        return render_template('redesigned_ui.html', original_text=user_input, redesigned_text=redesigned_ui)

    return render_template('ui_redesign_form.html')


# Book Recommendation route
@app.route('/recommend_book', methods=['GET'])
def recommend_book():
    books = Book.query.all()

    # Extract book titles from the library
    book_titles = [book.title for book in books]

    # Concatenate book titles into a single string
    books_text = '\n'.join(book_titles)

    # Call ChatGPT to get a book recommendation
    recommendation = get_recommendation_from_chatgpt(books_text)

    return render_template('recommendation.html', recommendation=recommendation)


# Home page
@app.route('/')
def home():
    books = Book.query.all()
    authors = Author.query.all()
    return render_template('home.html', books=books, authors=authors)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
