import parse_timetable_helpers
import json
import utils
import time

print("Loading timetable...")
with open("timetable.txt", "r", encoding="windows-1250") as file:
    lines = file.readlines()

bus_numbers = parse_timetable_helpers.get_bus_numbers(lines)

print("Parsing bus numbers...")
with open("data/bus_numbers.json", "w") as file:
    json.dump(bus_numbers, file)
print("Parsing bus stops...")
stops = parse_timetable_helpers.get_stops(lines)
print("Parsing bus routes...")
routes = {}
for bus_number in bus_numbers:
    routes[bus_number] = parse_timetable_helpers.get_route_ids(lines, bus_number, stops)
with open("data/routes.json", "w") as file:
    json.dump(routes, file)

with open("data/stops.json", "w") as file:
    json.dump(stops, file)
for number in bus_numbers:
    print("Parsing timetables for bus number: ", number)
    routes = parse_timetable_helpers.get_routes_timetables(lines, number)
    with open("data/timetables/" + number + ".json", "w") as file:
        json.dump(routes, file)
    print("Finished parsing timetables for bus number: ", number)