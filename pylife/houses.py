import re
import urllib.request

from bs4 import BeautifulSoup
from pylife.utils import parse_date, is_float

PRICE_REGEX = r"^\D*(\d+(?:\.\d+)?)"
DATE_REGEX = r"[0-9]{4}-(?:0[1-9]|1[0-2])-(?:0[1-9]|[1-2][0-9]|3[0-1])"

custom_headers = {
    "Referer": "http://panel.pylife.pl/domy",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0"
}


def get_houses():
    request = urllib.request.Request("http://panel.pylife.pl/domy", headers=custom_headers)
    page = urllib.request.urlopen(request)
    bs4 = BeautifulSoup(page, "html.parser")

    table = bs4.find("table", {"id": "tdomy"})
    houses = []

    for row in table.find("tbody").find_all("tr"):
        data = row.find_all("td")
        house = {
            "id": int(row["hid"]),
            "x": int(float(row["x"])),
            "y": int(float(row["y"])),
            "name": data[0].string,
            "location": data[1].string,
            "owner": data[2].string if data[2].string != "Do wynajęcia" else None,
            "price": data[3].string if is_float(data[3].string) else False,
            "expiry": None
        }

        houses.append(house)

    return houses


def get_house_details(id: int):
    request = urllib.request.Request("http://panel.pylife.pl/domy/" + str(id), headers=custom_headers)
    page = urllib.request.urlopen(request)
    bs4 = BeautifulSoup(page, "html.parser")

    body = bs4.find("div", {"id": "m_domy"})
    details = {}

    for tag in body.find_all(text=True):
        if "za dobę" in tag.string:
            details["price"] = float(re.findall(PRICE_REGEX, tag.string)[0])
        elif "Dom jest opłacony do" in tag.string:
            details["expiry"] = parse_date(re.findall(DATE_REGEX, tag.string)[0])

    return details
