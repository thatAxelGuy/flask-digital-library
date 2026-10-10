"""Digital library app."""

from datetime import date
from pathlib import Path

from flask import Flask, render_template, request
from sqlalchemy.exc import SQLAlchemyError

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
    books = db.session.execute(db.select(Book)).scalars().all()
    # name = request.args.get("name", "Flask")
    # return f"Hello, {escape(name)}!"
    return render_template("home.html", books=books)


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    """Create a new author from the form submission and render the page."""
    message = None

    if request.method == "POST":
        author = Author()
        name = request.form["name"].strip()
        if name:
            author.name = name

        raw_birthdate = request.form["birthdate"]
        if raw_birthdate:
            author.birthdate = date.fromisoformat(raw_birthdate)

        raw_date_of_death = request.form["date_of_death"]
        if raw_date_of_death:
            author.date_of_death = date.fromisoformat(raw_date_of_death)
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
