from geopy.geocoders import MapBox
from geopy.exc import GeocoderTimedOut
import json
import csv

# initialize MapBox API 
geolocator = MapBox(api_key="pk.eyJ1Ijoic2FjaDgxNDEiLCJhIjoiY2x1cXQ2MGdlMDFyYTJsbzJpd2k2c2hrZCJ9.Exjb8uFz7gboyXpa4MlNVw")

with open('../project_nurture/public/coordinates.json', 'r') as file:
    data = json.load(file)

# Extract the coordinates into a list
coordinates = [(item['Latitude'], item['Longitude']) for item in data]
 
with open('coordinates_with_city_state.csv', 'w', newline='') as csvfile:
    fieldnames = [ 'Area', 'State', 'Latitude', 'Longitude']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for i, coord in enumerate(coordinates, start=1):
        retries = 1000 # Number of retries for a coordinate
        while retries > 0:
            try:
                # Format the coordinates as a string separated by a comma
                coord_str = f"{coord[0]},{coord[1]}"
                                
                # Reverse geocode the coordinates
                location = geolocator.reverse(coord_str, exactly_one=True)
                
                # Extract area and state from the address string
                address_parts = location.address.split(', ')
                area = address_parts[-3]
                state = address_parts[-2]
                
                # Write to CSV
                writer.writerow({'Area': area, 'State': state, 'Latitude': coord[0], 'Longitude': coord[1]})
                
                print("Processed 1 coordinate." if i == 1 else f"Processed {i} coordinates.")
                break # Break the loop if successful
            except GeocoderTimedOut as e:
                print(f"Service timed out for coordinate {coord}. Retrying...")
                retries -= 1
            except Exception as e:
                print(f"Error processing coordinate {coord}: {e}")
                break # Break the loop if an unexpected error occurs
print("Done!")