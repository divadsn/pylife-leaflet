from flask import Blueprint, jsonify, abort

from pylife.models import Zone, House
from pylife.utils import parse_zone

mod = Blueprint("points", __name__, url_prefix="/points")


@mod.route("zones", methods=["GET"])
def get_zones():
    zones = Zone.query.order_by(Zone.id).all()
    data = []

    if not zones:
        # something is wrong with the database
        return abort(503)

    for zone in zones:
        points = parse_zone(zone.points)
        data.append({
            "id": zone.id,
            "name": zone.name,
            "points": points
        })

    return jsonify({"data": data})


@mod.route("houses", methods=["GET"])
def get_houses():
    houses = House.query.order_by(House.id).all()
    data = []

    if not houses:
        # something is wrong with the database
        return abort(503)

    for house in houses:
        data.append({
            "id": house.id,
            "name": house.name,
            "x": 3000 + house.x,
            "y": 3000 - house.y,
            "location": house.location,
            "owner": house.owner,
            "price": house.price,
            "expiry": house.expiry,
            "last_update": house.last_update
        })

    last_update = House.query.with_entities(House.last_update).order_by(House.last_update.desc()).first()[0]
    return jsonify({"data": data, "last_update": last_update})
