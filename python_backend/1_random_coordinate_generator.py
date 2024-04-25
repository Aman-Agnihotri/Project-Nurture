import pycristoforo as pyc
import json
import csv

from geopy.geocoders import MapBox
from geopy.exc import GeocoderTimedOut

# initialize MapBox API 
geolocator = MapBox(api_key="pk.eyJ1Ijoic2FjaDgxNDEiLCJhIjoiY2x1cXQ2MGdlMDFyYTJsbzJpd2k2c2hrZCJ9.Exjb8uFz7gboyXpa4MlNVw")

country = pyc.get_shape("India")

points = []
coordinates_list = []
states_in_main_data = []

with open('./Minor2data.csv', 'r') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        state_name = row['State']
        states_in_main_data.append(state_name)
        
# print(states_in_main_data)
        
i = 0

print("Starting the coordinate gathering...")
for state_main in states_in_main_data:
    j=1
    successful = False
    while not successful:
        retries = 100 # Number of retries for a coordinate
        while retries > 0:
            try:
                point = pyc.geoloc_generation(country, 1, "India")
                coordinate = []
                
                for point_check in point:
                    coordinate = point_check["geometry"]["coordinates"]
                    
                    # Format the coordinates as a string separated by a comma
                    coord_str = f"{coordinate[1]},{coordinate[0]}"
                    
                    # Reverse geocode the coordinates
                    location = geolocator.reverse(coord_str, exactly_one=True)
                    
                    # Extract area and state from the address string
                    address_parts = location.address.split(', ')
                    state = address_parts[-2]
                    # print(state)
                    
                    
                    if state == state_main:
                        points.append(point)
                        successful = True
                        i+=1
                        if i == 1:
                            print(f"Success! Found {i} coordinate.")
                        else:
                            print(f"Success! Found {i} coordinates.")
                        break
            except GeocoderTimedOut as e:
                    print("Service timed out for coordinate. Retrying...")
                    retries -= 1
            except Exception as e:
                    print(f"Error processing coordinate : {e}")
                    break
                    
for point in points:
    coordinates = point["geometry"]["coordinates"]
    latitude = coordinates[1]
    longitude = coordinates[0]
    coordinates_list.append({"Latitude": latitude, "Longitude": longitude})

with open('coordinates.json', 'w') as f:
    json.dump(coordinates_list, f)