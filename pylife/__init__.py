from flask import Flask, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy

# Init app
app = Flask(__name__, instance_relative_config=False, static_url_path="")
app.config.from_object("config")

# Load database
db = SQLAlchemy(app)

from pylife.views import points, search

# Register routes
app.register_blueprint(points.mod)
app.register_blueprint(search.mod)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("images/favicon.png")


@app.route("/assets/<path:filename>")
def get_asset(filename):
    return send_from_directory("assets/", filename)
