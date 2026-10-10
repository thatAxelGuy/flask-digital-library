"""Digital library app."""

from datetime import date
from pathlib import Path

from flask import Flask, redirect, render_template, request, url_for
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from data_models import Author, Book, db

app = Flask(__name__)

basedir = Path(__file__).resolve().parent
data = basedir / "data"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{data}/library.sqlite"

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    """Show the home page."""
    message = request.args.get("message")
    sort = request.args.get("sort", "title")  # sort by "title" is the default
    search = request.args.get("q", "").strip()

    stmt = db.select(Book).join(Book.author)

    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Book.title.ilike(pattern), Author.name.ilike(pattern))
        )

    if sort == "title":
        stmt = stmt.order_by(Book.title)
    elif sort == "author":
        stmt = stmt.order_by(Author.name, Book.title)
    elif sort == "year":
        stmt = stmt.order_by(Book.publishing_year)

    books = db.session.scalars(stmt).all()

    return render_template(
        "home.html", books=books, search=search, message=message, sort=sort
    )


def _parse_optional_date(date_str: str) -> date | None:
    if not date_str:
        return None
    return date.fromisoformat(date_str)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Create a new author from the form submission and render the page."""
    message = None

    if request.method == "POST":
        author = Author()
        name = request.form["name"].strip()
        if name:
            author.name = name

        author.birthdate = _parse_optional_date(request.form["birthdate"])

        author.date_of_death = _parse_optional_date(
            request.form["date_of_death"]
        )
        try:
            db.session.add(author)
            db.session.commit()
            message = f"Added {author.name} to the library."
        except SQLAlchemyError as e:
            print(f"Error: {e} while saving author.")

            # reset the session so later requests still work
            db.session.rollback()
            message = "Could not save the author. Please try again."

    return render_template("add_author.html", message=message)


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    """Create a new book from the form submission and render the page."""
    message = None
    authors = db.session.execute(db.select(Author)).scalars().all()

    if request.method == "POST":
        title = request.form["title"].strip()
        isbn = (
            request.form["isbn"]
            .strip()
            .replace("-", "")
            .replace(" ", "")
            .upper()
        )

        try:
            publishing_year = int(request.form["publishing_year"])
        except ValueError:
            publishing_year = None

        try:
            # Get author by id
            author = db.session.get(Author, int(request.form["author_id"]))
        except ValueError:
            author = None

        if not title:
            message = "Title is required."
        elif not isbn:
            message = "ISBN is required."
        elif not publishing_year:
            message = "Publishing year is required."
        elif not author:
            message = "Please choose an existing author."
        else:
            book = Book(
                title=title,
                isbn=isbn,
                publishing_year=publishing_year,
                author=author,
            )
            try:
                db.session.add(book)
                db.session.commit()
                message = f"Added {book.title} to the library."
            except IntegrityError:
                db.session.rollback()
                message = "A book with this ISBN already exists."
            except SQLAlchemyError:
                db.session.rollback()
                message = "Could not save the book. Please try again."

    return render_template("add_book.html", message=message, authors=authors)


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id: int):
    """Delete book by id if it exists."""
    message = None
    book = db.session.get(Book, book_id)
    if book is None:
        message = "Book doesn't exist"
    else:
        db.session.delete(book)
        db.session.commit()
        message = f"Successfully deleted {book.title} from library."
    return redirect(url_for("index", message=message))


@app.route("/author/<int:author_id>/delete", methods=["POST"])
def delete_author(author_id: int):
    """Delete author by id if they exist."""
    message = None
    author = db.session.get(Author, author_id)
    if author is None:
        message = "Author doesn't exist"
    else:
        db.session.delete(author)
        db.session.commit()
        message = f"Successfully deleted {author.name} from database."
    return redirect(url_for("index", message=message))
