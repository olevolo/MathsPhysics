import math
import json

def distance(a, b):
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

def is_between(a, c, b):
    return math.isclose(distance(a, c) + distance(c, b), distance(a, b))

def read_json(filepath):
    with open(filepath) as f:
        return json.load(f)

def tri_area(triangle):
    a = distance(triangle[0], triangle[1])
    b = distance(triangle[1], triangle[2])
    c = distance(triangle[2], triangle[0])

    p = (a + b + c) / 2

    return math.sqrt(p*(p-a)*(p-b)*(p-c))


