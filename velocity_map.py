#Api-key:6d2d6b9f-5ab6-471f-8abc-d389e007d22b
import requests
import utils
import handle_bus_data as bus
import json
import time
import sys
import os
import folium


file_path = './data/' + sys.argv[1] + '.json'
with open(file_path, 'r+') as file:
    data = json.load(file)
vehicle_numbers = bus.get_vehicle_numbers(data)
speeds_over_50 = []
total_vehicle_numbers = len(vehicle_numbers)
exceeding_speed_vehicles = 0
squares_total_buses = dict()
for vehicle_number in vehicle_numbers:
    records = bus.get_vehicle_records(data, vehicle_number)
    speeds = bus.average_speeds(records)
    for speed in speeds:
        #Eliminating speeds coming from GPS errors
        if 100 > speed['Speed'] > 50:
            exceeding_speed_vehicles += 1
            speeds_over_50.append(speed)
            break
    for speed in speeds:
        lat = speed['Lat']
        lon = speed['Lon']
        lat = int(lat * 200)
        lon = int(lon * 100)
        if (lat, lon) in squares_total_buses:
            squares_total_buses[(lat, lon)] += 1
        else:
            squares_total_buses[(lat, lon)] = 1
print("There are", exceeding_speed_vehicles, "vehicles that exceeded 50 km/h out of", total_vehicle_numbers, "vehicles.")

squares = dict()
for speed in speeds_over_50:
    lat = speed['Lat']
    lon = speed['Lon']
    lat = int(lat * 200)
    lon = int(lon * 100)
    if (lat, lon) in squares:
        squares[(lat, lon)] += 1
    else:
        squares[(lat, lon)] = 1
max_value = max(squares.values())
m = folium.Map(location=[52.22977, 21.01178], zoom_start=12)

max_percentage = 0
for (key, value) in squares.items():
    folium.Rectangle(
        bounds=[[key[0] / 200, key[1] / 100], [(key[0] + 1) / 200, (key[1] + 1) / 100]],
        color='transparent',
        fill=True,
        fill_color='red',
        fill_opacity=value / squares_total_buses[key] * 0.8,
    ).add_to(m)
    max_percentage = max(max_percentage, value / squares_total_buses[key])
print("Max percentage of buses exceeding speed in a single rectangle:", max_percentage * 100, "%")
m.save('map.html')