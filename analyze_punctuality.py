import parse_timetable_helpers as pt
import handle_bus_data as bus
import utils
import json
import folium
import sys
import load_data as ld
import datetime

(data, stops, routes) = ld.load_data(sys.argv)
all_real_routes = bus.get_all_bus_number_real_routes(stops, routes, data, '105')
for route in all_real_routes:
    for real_route in route:
        print("Next real route:")
        for stop in real_route:
            print(stops[stop['id']]['name'], stop['expected_time'], "Delay:", stop['delay'])
    print('\n')
    print('___________________________')
# vehicle_numbers = bus.get_vehicle_numbers(data)
# bus_number = '186'
# vehicles_with_line = bus.get_buses_by_line(data, bus_number)
# bus_records = bus.get_vehicle_records(data, vehicles_with_line[4]['VehicleNumber'])
# bus_records = bus.add_halfway_points(bus_records)
# closest_stops = bus.assign_closest_stops(bus_records, routes, stops)
# intervals = bus.get_stops_time_intervals(stops, closest_stops)
# routes_105 = routes[bus_number]
# route_times = bus.match_route_to_stop_intervals(stops, routes_105[0], intervals)[0]
# # def get_predicted_times(stops, routes, bus_number, stop_id, time):
# scheduled_route_times = bus.get_predicted_times(stops, routes, bus_number, routes_105[0][0]['id'], utils.convert_time(route_times[0]['end_time']))
# # print("Scheduled times",routes_105[1][0])
# for i in range(len(scheduled_route_times)):
#     if scheduled_route_times[i] is not None:
#         print(len(scheduled_route_times[i]), len(route_times))
#         for j in range(len(scheduled_route_times[i])):
#             print(stops[scheduled_route_times[i][j]['id']]['name'], scheduled_route_times[i][j]['time'], route_times[j]['start_time'], route_times[j]['end_time'])
# m = folium.Map(location=[52.22977, 21.01178], zoom_start=12)
# for record in closest_stops:
#     folium.Marker([record['Lat'], record['Lon']], popup=stops[record['ClosestStop']]["name"]).add_to(m)
# m.save('map.html')

#Show trace of bus of id 2250 on the map

