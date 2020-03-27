from flask import Flask, render_template, send_from_directory
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy

# Init app
app = Flask(__name__, instance_relative_config=False)
app.config.from_object("config")

# Init web assets
assets = Environment(app)
assets.register("css_map", Bundle("css/leaflet.css", "css/map.css", filters="cssmin", output="css/map.bundle.css"))
assets.register("js_map", Bundle("js/leaflet.js", "js/leaflet-rastercoords.js", "js/map.js", filters="jsmin", output="js/map.bundle.js"))

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


@app.route("/tiles/<z>/<x>/<y>.png")
def get_tilemap(z, x, y):
    return send_from_directory(f"tiles/{z}/{x}/", f"{y}.png")
