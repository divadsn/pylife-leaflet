from flask import Blueprint, jsonify, abort

from shapely.geometry import box
from shapely.ops import cascaded_union

from pylife.models import Zone, ZoneName, House

mod = Blueprint("points", __name__, url_prefix="/points")


@mod.route("zones", methods=["GET"])
def get_zones():
    zones = Zone.query.order_by(Zone.name).all()
    polygons = {}

    if not zones:
        # something is wrong with the database
        return abort(503)

    for zone in zones:
        polygon = box(3000 + zone.x1, 3000 - zone.y1, 3000 + zone.x2, 3000 - zone.y2)

        if zone.name in polygons:
            polygons[zone.name].append(polygon)
        else:
            polygons[zone.name] = [polygon]

    # contains id mapping for search
    names = ZoneName.query.all()
    data = []

    for name in names:
        union = cascaded_union(polygons[name.name])

        if union.geom_type == "MultiPolygon":
            coordinates = [[point for point in polygon.exterior.coords] for polygon in list(union)]
        else:
            coordinates = [point for point in union.exterior.coords]

        data.append({
            "id": name.id,
            "name": name.name,
            "coordinates": coordinates
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
            "x": 3000 + house.x,
            "y": 3000 - house.y,
            "name": house.name,
            "location": house.location,
            "owner": house.owner,
            "price": house.price,
            "expiry": house.expiry,
            "last_update": house.last_update
        })

    last_update = House.query.with_entities(House.last_update).order_by(House.last_update.desc()).first()[0]
    return jsonify({"data": data, "last_update": last_update})
