"""Digital library app."""

from pathlib import Path

from flask import Flask, render_template

from data_models import db

app = Flask(__name__)

basedir = Path(__file__).resolve().parent
data = basedir / "data"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{data}/library.sqlite"

db.init_app(app)


@app.route("/")
def index():
    """Show the home page."""
    # name = request.args.get("name", "Flask")
    # return f"Hello, {escape(name)}!"
    return render_template("home.html")
