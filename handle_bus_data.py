import utils
import parse_timetable_helpers as pt
import json
from datetime import datetime
import folium
from functools import cmp_to_key

def get_buses_by_line(data, line):
    buses = []
    for bus in data:
        if bus['Lines'] == line:
            buses.append(bus)
    return buses
def get_vehicle_numbers(data):
    vehicle_numbers = set()
    for bus in data:
        vehicle_numbers.add(bus['VehicleNumber'])
    l = list(vehicle_numbers)
    l.sort()
    return l
def get_bus_line_vehicle_numbers(data, line):
    vehicle_numbers = set()
    for bus in data:
        if bus['Lines'] == line:
            vehicle_numbers.add(bus['VehicleNumber'])
    l = list(vehicle_numbers)
    l.sort()
    return l

#Get all records of a vehicle sorted by time
def get_vehicle_records(data, vehicle_number):
    records = []
    for bus in data:
        if bus['VehicleNumber'] == vehicle_number:
            records.append(bus)
    records.sort(key=lambda x: x['Time'])
    return records
def average_speeds(records):
    speeds = []
    for i in range(len(records) - 1):
        time1 = records[i]['Time']
        time2 = records[i + 1]['Time']
        time_diff = utils.time_difference_in_hours(time1, time2)
        distance = utils.distance_in_kilometers(records[i]['Lat'], records[i]['Lon'], records[i + 1]['Lat'], records[i + 1]['Lon'])
        if time_diff == 0:
            continue
        speeds.append({
            'Lat': (records[i]['Lat'] + records[i + 1]['Lat']) / 2,
            'Lon': (records[i]['Lon'] + records[i + 1]['Lon']) / 2,
            'Speed': distance / time_diff,
            'Time': utils.average_time(time1, time2)
        })
    return speeds
def get_vehicle_numbers(data):
    vehicle_numbers = set()
    for bus in data:
        vehicle_numbers.add(bus['VehicleNumber'])
    l = list(vehicle_numbers)
    l.sort()
    return l

def find_mathcing_scheduled_departure_time_first_stop(timetable, time):
    #Given real time of departure finds the matching scheduled time of departure (assume the bus arrives not earlier than 2 minutes before the scheduled time)
    for i in range(len(timetable) - 1):
        if utils.time_is_between(time, utils.add_time(timetable[i], {"hours": 0, "minutes": -2}), utils.add_time(timetable[i + 1], {"hours": 0, "minutes": -2})):
            return timetable[i]
    return timetable[-1]
        
def get_min_times_from_previous_stop(route):
    min_times = []
    min_times.append({
        "id": route[0]['id'],
        "min_time": {
            "hours": 0,
            "minutes": 0
        }
    })
    for i in range(1, len(route)):
        min_times.append({
            "id": route[i]['id'],
            #We assume that minimal time between stops is the difference between the minimal scheduled times of arrival at the stops
            "min_time": utils.subtract_time(route[i]['min_time'], route[i - 1]['min_time'])
        })
    return min_times

def route_matches_timetable(route, timetable):
    if len(route) - 1 != len(timetable):
        return False
    for i in range(len(timetable)):
        if route[i]['id'] != timetable[i]['id']:
            return False
    return True

def find_earliest_time_after(times, time):
    for i in range(len(times) - 1):
        if utils.time_is_between(time, times[i], times[i + 1]):
            if time == times[i]:
                return times[i]
            return times[i + 1]
    return times[0]

def get_predicted_times_single_route(stops, route, bus_number, stop_id, time, timetable):
    if stop_id != timetable[0]['id']:
        return None
    scheduled_start_time = find_mathcing_scheduled_departure_time_first_stop(timetable[0]['timetable'], time)
    predicted_times = []
    predicted_times.append({
        "id": route[0]['id'],
        "time": scheduled_start_time
    })
    min_times_between = get_min_times_from_previous_stop(route)
    for i in range(1, len(timetable)):
        time = find_earliest_time_after(timetable[i]['timetable'], utils.add_time(predicted_times[i - 1]['time'], min_times_between[i]['min_time']))
        min_time = utils.add_time(scheduled_start_time, utils.subtract_time(route[i]['min_time'], route[1]['min_time']))
        max_time = utils.add_time(scheduled_start_time, route[i]['max_time'])
        if utils.time_is_between(time, min_time, max_time):
            predicted_times.append({
                "id": route[i]['id'],
                "time": time
            })
        else:
            return None
    predicted_times.append({
        "id": route[-1]['id'],
        "time": utils.add_time(predicted_times[-1]['time'], min_times_between[-1]['min_time'])
    })
    return predicted_times


#Given arrival time of a bus at a first stop returns possible times of arrival at the next stops in possible routes
def get_predicted_times(stops, routes, bus_number, stop_id, time):
    routes_times = []
    with open("data/timetables/" + bus_number + ".json", "r") as file:
        timetables = json.load(file)
    routes = routes[bus_number]
    for i in range(len(timetables)):
        route_timetable = timetables[i]
        route_index = -1
        for j in range(len(routes)):
            if route_matches_timetable(routes[j], route_timetable):
                route_index = j
                break
        routes_times.append(get_predicted_times_single_route(stops, routes[route_index], bus_number, stop_id, time, route_timetable))
    return routes_times

#Add points in the middle of between two consecutive records to make the route more accurate
def add_halfway_points(sorted_records):
    extended_records = []
    for i in range(len(sorted_records) - 1):
        extended_records.append(sorted_records[i])
        extended_records.append({
            'Lines': sorted_records[i]['Lines'],
            'VehicleNumber': sorted_records[i]['VehicleNumber'],
            'Lat': (sorted_records[i]['Lat'] + sorted_records[i + 1]['Lat']) / 2,
            'Lon': (sorted_records[i]['Lon'] + sorted_records[i + 1]['Lon']) / 2,
            'Time': utils.average_time(sorted_records[i]['Time'], sorted_records[i + 1]['Time'])
        })
    extended_records.append(sorted_records[-1])
    return extended_records

def get_stop_ids(routes):
    result = set()
    for route in routes:
        for stop in route:
            result.add(stop['id'])
    return result
    
def assign_closest_stops(records, routes, stops):
    current_bus_number = '-1'
    for record in records:
        min_distance = float("inf")
        closest_stop_id = '-1'
        bus_number = record['Lines']
        if bus_number != current_bus_number:
            current_bus_number = bus_number
            routes_bus_number = routes[bus_number]
            possible_stops = get_stop_ids(routes_bus_number)
        for stop_id in possible_stops:
            full_stop_data = stops[stop_id]
            distance = utils.distance_in_kilometers(record['Lat'], record['Lon'], float(full_stop_data['Lat']), float(full_stop_data['Lon']))
            if distance < min_distance:
                min_distance = distance
                closest_stop_id = stop_id
        record['ClosestStop'] = closest_stop_id
    return records


#Gives the time intervals of stops at a bus
def get_stops_time_intervals(stops, records):
    intervals = []
    current_stop = "-1"
    current_line = "-1"
    for i in range(len(records) - 1):
        if i == 0:
            current_stop = records[i]['ClosestStop']
            current_line = records[i]['Lines']
            current_beginning = records[i]['Time']
        else:
            if stops[records[i]['ClosestStop']]["name"] != stops[current_stop]["name"] or records[i]['Lines'] != current_line:
                intervals.append({
                    "id": current_stop,
                    "start_time": current_beginning,
                    "end_time": records[i - 1]['Time'],
                    "line": current_line
                })
                current_stop = records[i]['ClosestStop']
                current_line = records[i]['Lines']
                current_beginning = records[i]['Time']
    intervals.append({
        "id": current_stop,
        "start_time": current_beginning,
        "end_time": records[-1]['Time'],
        "line": current_line
    })
    return intervals

#Given a route and intervals of stops gives the route
def match_route_to_stop_intervals(stops, route, intervals, debug):
    BREAK_COND = 10
    j = 0
    matched_routes = []
    break_counter = 0
    current_route = []
    for i in range(len(intervals)):
        if j != 0:
            if stops[intervals[i]['id']]["name"] == stops[route[j]['id']]["name"]:
                while stops[intervals[i]['id']]["name"] == stops[route[j]['id']]["name"]:
                    current_route.append(intervals[i])
                    break_counter = 0
                    j += 1
                    if j == len(route):
                        matched_routes.append(current_route)
                        current_route = []
                        break_counter = 0
                        j = 0
                        continue
            else:
                if debug:
                    for interval in intervals:
                        print(stops[interval['id']]['name'], interval['start_time'], interval['end_time'])
                    print("\n\n\n")
                if j < len(route) - 1:
                    #We assume that the record didn't cover the stop so we add the stop with the time of the next stop
                        if stops[intervals[i]['id']]["name"] == stops[route[j + 1]['id']]["name"]:
                            current_route.append({
                                "id": route[j]['id'],
                                "start_time": intervals[i]['start_time'],
                                "end_time": intervals[i]['end_time']
                            })
                            j += 1
                            break_counter = 0
                            current_route.append(intervals[i])
                            j += 1

                break_counter += 1
                if break_counter == BREAK_COND:
                    j = 0
                    current_route = []
                    break_counter = 0
        else:
            if stops[intervals[i]['id']]["name"] == stops[route[j]['id']]["name"]:
                while stops[intervals[i]['id']]["name"] == stops[route[j]['id']]["name"]:
                    current_route.append(intervals[i])
                    break_counter = 0
                    j += 1
                    if j == len(route):
                        matched_routes.append(current_route)
                        current_route = []
                        break_counter = 0
                        j = 0
                        continue
        if j == len(route):
            matched_routes.append(current_route)
            current_route = []
            break_counter = 0
            j = 0
    return matched_routes

#Given records of a bus making a route adds the expected departure times
def add_expected_departure_times(stops, routes, real_route, bus_number):
    real_route_extended = real_route.copy()
    predicted_times_routes = get_predicted_times(stops, routes, bus_number, real_route[0]['id'], utils.convert_time(real_route[0]['end_time']))
    for i in range(len(predicted_times_routes)):
        if predicted_times_routes[i] is not None:
            #Check if real_route matches the predicted route
            mathces = True
            for j in range(len(predicted_times_routes[i])):
                if stops[predicted_times_routes[i][j]['id']]["name"] != stops[real_route[j]['id']]["name"]:
                    mathces = False
                    break
            if not mathces:
                continue
            for j in range(len(predicted_times_routes[i])):
                time_diff = utils.subtract_time(utils.convert_time(real_route_extended[j]['start_time']),predicted_times_routes[i][j]['time'])
                if time_diff['hours'] > 12:
                    time_diff = {"hours": 0, "minutes": 0}
                real_route_extended[j]['delay'] = max(0, time_diff["minutes"])
                real_route_extended[j]['expected_time'] = predicted_times_routes[i][j]['time']
            return real_route_extended

#Get all records of routes made by buses of a given number
def get_all_bus_number_real_routes(stops, routes, data, bus_number):
    i = 0
    vehicles_with_line = get_bus_line_vehicle_numbers(data, bus_number)
    routes_bus_number = routes[bus_number]
    real_routes_for_bus_number = []
    show_on_map = 0
    for route in routes_bus_number:
        real_routes_for_route = []
        i += 1
        print("Route", i, "out of", len(routes_bus_number))
        for vehicle in vehicles_with_line:
            records = get_vehicle_records(data, vehicle)
            records = add_halfway_points(records)
            closest_stops = assign_closest_stops(records, routes, stops)
            intervals = get_stops_time_intervals(stops, closest_stops)
            route_times = match_route_to_stop_intervals(stops, route, intervals, False)
            for route_time in route_times:
                route_time = add_expected_departure_times(stops, routes, route_time, bus_number)
                real_routes_for_route.append(route_time)
            real_routes_for_route = [route for route in real_routes_for_route if route is not None]
            real_routes_for_route.sort(key=lambda x: utils.convert_to_datetime(x[0]['start_time']))
        real_routes_for_bus_number.append(real_routes_for_route)
    return real_routes_for_bus_number


        
        


            
