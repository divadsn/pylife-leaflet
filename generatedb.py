#!/usr/bin/env python3
import re
import json
import urllib.request

from sqlalchemy import exc

from shapely.geometry import box
from shapely.ops import unary_union
from bs4 import BeautifulSoup

from pylife import db
from pylife.models import Zone, House, Blip, Event  # noqa: F401

MTA_ZONENAMES = "https://github.com/multitheftauto/mtasa-blue/raw/master/Shared/mods/deathmatch/logic/CZoneNames.cpp"
ZONE_REGEX = r"{(-?\d+), (-?\d+), (?:-?\d+), (-?\d+), (-?\d+), (?:-?\d+), \"(.*?)\"}"

zones = {}


def main():
    try:
        db.drop_all()
    except exc.SQLAlchemyError:
        pass

    # Creating tables
    print("Creating new tables in database...")
    db.create_all()

    # Load zone names mapping
    load_zone_names()

    # Generating data
    generate_zones()
    generate_houses()
    generate_blips()

    # Saving new data to database
    db.session.commit()

    # Fixing timestamp precision
    db.engine.execute("ALTER TABLE houses ALTER last_update TYPE timestamp(0)")


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def load_zone_names():
    with open("data/zonenames.txt") as f:
        for line in f.readlines():
            zone_id = int(line.split(",")[0])
            zones[zone_id] = {
                "name": line.split(",")[1],
                "description": line.split(",")[2].rstrip(),
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
        union = unary_union(zone["polygons"])

        # Check if union has more than one polygon
        if union.geom_type == "MultiPolygon":
            points = [[(int(point[0]), int(point[1])) for point in polygon.exterior.coords] for polygon in list(union)]
        else:
            points = [(int(point[0]), int(point[1])) for point in union.exterior.coords]

        print(f"Adding zone \"{zone['name']}\" with ID {index} to database...")
        db.session.add(Zone(id=index, name=zone["name"], description=zone["description"], points=json.dumps(points)))


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

    # Sort dict items by id ascending
    houses = {k: houses[k] for k in sorted(houses)}

    for index, house in houses.items():
        print(f"Adding house \"{house['name']}\" with ID {index} to database...")
        db.session.add(House(id=index, x=house["x"], y=house["y"], name=house["name"], location=house["location"],
                             owner=house["owner"], price=house["price"], expiry=house["expiry"]))


def generate_blips():
    print("Generating table for blips...")

    with open("data/blips.txt") as f:
        blips = []

        for line in f.readlines():
            line = line.rstrip()
            if line == "" or line.startswith("#"):
                continue

            blip = line.split(",")
            blips.append({
                "x": int(float(blip[0])),
                "y": int(float(blip[1])),
                "name": blip[2],
                "icon": blip[3]
            })

    for blip in blips:
        print(f"Adding blip \"{blip['name']}\" at ({blip['x']}, {blip['y']}) to database...")
        db.session.add(Blip(x=blip["x"], y=blip["y"], name=blip["name"], icon=blip["icon"]))


if __name__ == "__main__":
    main()
