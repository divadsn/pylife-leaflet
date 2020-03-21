import datetime
import pytz


def parse_date(date):
    tz = pytz.timezone("Europe/Warsaw")
    return tz.localize(datetime.datetime.strptime(date, "%Y-%m-%d"))


def is_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
