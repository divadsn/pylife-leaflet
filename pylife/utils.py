import json


def parse_zone(data: str):
    points = json.loads(data)

    if len(points[0]) == 2:
        points = [points]

    points = [[{"x": 3000 + point[0], "y": 3000 - point[1]} for point in points] for points in points]
    return points[0] if len(points) == 1 else points
