import json


def parse_zone(data: str, is_raw: bool):
    points = json.loads(data)

    # Check if array is a polygon containing points
    if len(points[0]) == 2:
        points = [points]

    if is_raw:
        points = [[{"x": point[0], "y": point[1]} for point in polygon] for polygon in points]
    else:
        points = [[{"x": 3000 + point[0], "y": 3000 - point[1]} for point in polygon] for polygon in points]

    return points[0] if len(points) == 1 else points
