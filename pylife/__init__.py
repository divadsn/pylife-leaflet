from flask import Flask, render_template, send_from_directory
from flask_assets import Environment, Bundle
from flask_sqlalchemy import SQLAlchemy

# Init app
app = Flask(__name__, instance_relative_config=False)
app.config.from_object("config")

# Init web assets
assets = Environment(app)
assets.register("css_map", Bundle("css/leaflet.css", "css/leaflet-responsive-popup.css", "css/map.css",
                                  filters="cssmin", output="css/map.bundle.css"))
assets.register("js_map", Bundle("js/leaflet.js", "js/leaflet-rastercoords.js", "js/leaflet-responsive-popup.js",
                                 "js/dayjs.min.js", "js/map.js", filters="jsmin", output="js/map.bundle.js"))

# Load database
db = SQLAlchemy(app)

from pylife.views import points, search, lookup, widget  # noqa: E402

# Register routes
app.register_blueprint(points.mod)
app.register_blueprint(search.mod)
app.register_blueprint(lookup.mod)
app.register_blueprint(widget.mod)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon/favicon.ico")


@app.route("/tiles/<z>/<x>/<y>.png")
def get_tilemap(z, x, y):
    return send_from_directory(f"tiles/{z}/{x}/", f"{y}.png")
