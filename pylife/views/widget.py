from flask import Blueprint, render_template, abort
from pylife.models import House

mod = Blueprint("widget", __name__, url_prefix="/widget")


@mod.route("<house_id>")
def get_widget(house_id):
    house = House.query.get(house_id)

    if not house:
        abort(404)

    # Build the dict to jsonify later
    data = {
        "id": house.id,
        "name": house.name,
        "x": 3000 + house.x,
        "y": 3000 - house.y,
        "location": house.location,
        "owner": house.owner,
        "price": house.price,
        "expiry": house.expiry
    }

    return render_template("widget.html", data=data)
