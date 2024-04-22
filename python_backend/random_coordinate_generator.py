import pycristoforo as pyc
import json

country = pyc.get_shape("India")

points = pyc.geoloc_generation(country, 1385, "India")

# Assuming points is the list of points
coordinates_list = []

for point in points:
    coordinates = point["geometry"]["coordinates"]
    latitude = coordinates[1]
    longitude = coordinates[0]
    coordinates_list.append({"Latitude": latitude, "Longitude": longitude})

with open('/home/hunterhhh412/Local Stuff/Minor 2/Minor_2/malnutrition/public/coordinates.json', 'w') as f:
    json.dump(coordinates_list, f)