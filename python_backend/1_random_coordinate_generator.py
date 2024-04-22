import pycristoforo as pyc
import json

country = pyc.get_shape("India")

points = pyc.geoloc_generation(country, 1385, "India")

coordinates_list = []

for point in points:
    coordinates = point["geometry"]["coordinates"]
    latitude = coordinates[1]
    longitude = coordinates[0]
    coordinates_list.append({"Latitude": latitude, "Longitude": longitude})

with open('coordinates.json', 'w') as f:
    json.dump(coordinates_list, f)