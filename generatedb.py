#!/usr/bin/env python3
import re
import json
import urllib.request

from datetime import datetime
from sqlalchemy import exc

from shapely.geometry import box
from shapely.ops import cascaded_union
from bs4 import BeautifulSoup

from pylife import db
from pylife.models import Zone, House

MTA_ZONENAMES = "https://github.com/multitheftauto/mtasa-blue/raw/master/Shared/mods/deathmatch/logic/CZoneNames.cpp"
ZONE_REGEX = r"{(-?\d+), (-?\d+), (?:-?\d+), (-?\d+), (-?\d+), (?:-?\d+), \"(.*?)\"}"

zones = {}


def main():
    try:
        db.drop_all()
    except exc.SQLAlchemyError:
        print("Creating new tables in database...")
        pass

    # Creating tables
    db.create_all()

    # Load zone names mapping
    load_zone_names()

    # Generating data
    generate_zones()
    generate_houses()

    # Saving new data to database
    db.session.commit()


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def load_zone_names():
    with open("zonenames.txt") as f:
        for line in f.readlines():
            zone_id = int(line.split(",")[0])
            zones[zone_id] = {
                "name": line.split(",")[1].rstrip(),
                "polygons": []
            }


def get_id_by_name(name: str):
    for index, zone in zones.items():
        if zone["name"] == name:
            return index


def generate_zones():
    print("Generating table for zones...")

    with urllib.request.urlopen(MTA_ZONENAMES) as url:
        for line in url.readlines():
            matches = re.findall(ZONE_REGEX, str(line))
            if matches:
                zone = matches[0]
                zone_id = get_id_by_name(zone[4].replace("\\", ""))
                zones[zone_id]["polygons"].append(box(int(zone[0]), int(zone[1]), int(zone[2]), int(zone[3])))

    for index, zone in zones.items():
        union = cascaded_union(zone["polygons"])

        if union.geom_type == "MultiPolygon":
            points = [[(int(point[0]), int(point[1])) for point in polygon.exterior.coords] for polygon in list(union)]
        else:
            points = [(int(point[0]), int(point[1])) for point in union.exterior.coords]

        print(f"Adding zone \"{zone['name']}\" with ID {index} to database...")
        db.session.add(Zone(id=index, name=zone["name"], points=json.dumps(points)))


def generate_houses():
    print("Generating table for houses...")

    # Trying to avoid as much trouble as possbile by "mocking" a real browser request
    request = urllib.request.Request("http://panel.pylife.pl/domy", headers={
        "Referer": "http://panel.pylife.pl",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0"
    })

    with urllib.request.urlopen(request) as url:
        bs4 = BeautifulSoup(url, "html.parser")

        table = bs4.find("table", {"id": "tdomy"})
        houses = {}

        for row in table.find("tbody").find_all("tr"):
            house = row.find_all("td")
            house_id = int(row["hid"])
            houses[house_id] = {
                "x": int(float(row["x"])),
                "y": int(float(row["y"])),
                "name": house[0].string,
                "location": house[1].string,
                "owner": house[2].string if house[2].string != "Do wynajęcia" else None,
                "price": house[3].string if is_float(house[3].string) else 0.0,
                "expiry": None
            }

    houses = {k: houses[k] for k in sorted(houses)}

    for index, house in houses.items():
        print(f"Adding house \"{house['name']}\" with ID {index} to database...")
        db.session.add(House(id=index, x=house["x"], y=house["y"], name=house["name"], location=house["location"],
                             owner=house["owner"], price=house["price"], expiry=house["expiry"], last_update=datetime.utcnow()))


if __name__ == "__main__":
    main()