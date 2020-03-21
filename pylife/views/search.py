from flask import Blueprint, request, jsonify
from sqlalchemy import func

from pylife.models import ZoneName

mod = Blueprint("search", __name__)


@mod.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")

    zones = ZoneName.query.filter(func.lower(ZoneName.name).like(func.lower(f"%{query}%"))).limit(10).all()
    data = []

    for zone in zones:
        data.append({
            "id": zone.id,
            "name": zone.name
        })

    return jsonify(data)
