from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, url_for
import os

from data_models import db, Author, Book

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "5f352379324c22463451387a0aec5d2f"

db.init_app(app)

with app.app_context():
    db.create_all()


def parse_date(value):
    if value:
        return datetime.strptime(value, "%Y-%m-%d").date()
    return None


@app.route("/")
def home():
    sort = request.args.get("sort", "title")
    search = request.args.get("search", "").strip()

    query = Book.query.join(Author)

    if search:
        query = query.filter(Book.title.ilike(f"%{search}%"))

    if sort == "author":
        query = query.order_by(Author.name.asc())
    else:
        query = query.order_by(Book.title.asc())

    books = query.all()

    return render_template(
        "home.html",
        books=books,
        current_sort=sort,
        search=search
    )


@app.route("/add_author", methods=["GET", "POST"])
def add_author():
    if request.method == "POST":

        name = request.form.get("name")
        birthdate = request.form.get("birthdate")
        date_of_death = request.form.get("date_of_death")

        birth_date_obj = None
        death_date_obj = None

        if birthdate:
            birth_date_obj = datetime.strptime(
                birthdate, "%Y-%m-%d"
            ).date()

        if date_of_death:
            death_date_obj = datetime.strptime(
                date_of_death, "%Y-%m-%d"
            ).date()

        new_author = Author(
            name=name,
            birth_date=birth_date_obj,
            date_of_death=death_date_obj
        )

        db.session.add(new_author)
        db.session.commit()

        return render_template(
            "add_author.html",
            success_message="Author added successfully"
        )

    return render_template("add_author.html")


@app.route("/book/<int:book_id>/delete", methods=["POST"])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    author = book.author

    db.session.delete(book)
    db.session.commit()

    remaining_books = Book.query.filter_by(author_id=author.id).count()

    if remaining_books == 0:
        db.session.delete(author)
        db.session.commit()

    flash("Book deleted successfully", "success")

    return redirect(url_for("home"))


@app.route("/add_book", methods=["GET", "POST"])
def add_book():
    authors = Author.query.all()

    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        publication_year = request.form.get("publication_year")
        author_id = request.form.get("author_id")

        new_book = Book(
            isbn=isbn,
            title=title,
            publication_year=int(publication_year) if publication_year else None,
            author_id=int(author_id)
        )

        db.session.add(new_book)
        db.session.commit()

        return render_template(
            "add_book.html",
            authors=authors,
            success_message="Book added successfully"
        )

    return render_template("add_book.html", authors=authors)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)