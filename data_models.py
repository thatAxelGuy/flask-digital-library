"""SQLAlchemy models for the digital library."""

from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()


class Author(db.Model):
    """Represents an author in the library catalog."""

    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(200))
    birthdate: Mapped[date | None] = mapped_column(Date)
    date_of_death: Mapped[date | None] = mapped_column(Date)

    books: Mapped[list["Book"]] = relationship(
        back_populates="author", cascade="all, delete-orphan"
    )

    def __repr__(self):
        """Return a readable representation of the author."""
        return f"Author: name={self.name!r}, birthdate={self.birthdate!r}"


class Book(db.Model):
    """Represents a book in the library catalog."""

    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    isbn: Mapped[str] = mapped_column(String(20), unique=True)
    title: Mapped[str] = mapped_column(String(200))
    publishing_year: Mapped[int]
    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    author: Mapped["Author"] = relationship(back_populates="books")

    def __repr__(self):
        """Return a readable representation of the book."""
        return f"Book: name={self.title!r} by {self.author.name!r}"
