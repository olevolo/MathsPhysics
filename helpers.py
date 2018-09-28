import math
import json

def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def is_between(a, c, b):
    return math.isclose(distance(a, c) + distance(c, b), distance(a, b))

def read_json(filepath):
    with open(filepath) as f:
        return json.load(f)

