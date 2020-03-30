import json

from flask import Blueprint, request, jsonify, abort
from shapely.geometry import MultiPolygon, Polygon, Point

from pylife.models import Zone
from pylife.utils import CITY_NAMES

mod = Blueprint("lookup", __name__)


@mod.route("/lookup", methods=["GET"])
def lookup():
    x, y = request.args.get("x", type=int), request.args.get("y", type=int)

    if not x or not y:
        # bad request given
        return abort(400)

    zones = Zone.query.order_by(Zone.id).all()
    data = {
        "zone_name": None,
        "city_name": None
    }

    if not zones:
        # something is wrong with the database
        return abort(503)

    point = Point(x - 3000, 3000 - y)

    for zone in zones:
        points = json.loads(zone.points)

        if len(points[0]) == 2:
            polygon = Polygon(points)
        else:
            polygon = MultiPolygon([Polygon(polygon) for polygon in points])

        if polygon.contains(point):
            if zone.name in CITY_NAMES:
                data["city_name"] = zone.name
            else:
                data["zone_name"] = zone.name

    return jsonify(data)
