from flask import Blueprint, request, jsonify
from sqlalchemy import func

from pylife.models import Zone

mod = Blueprint("search", __name__)


@mod.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "")

    zones = Zone.query.filter(Zone.name.ilike(f"%{query}%")).limit(10).all()
    data = []

    for zone in zones:
        data.append({
            "id": zone.id,
            "name": zone.name
        })

    return jsonify(data)
