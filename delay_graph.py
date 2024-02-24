import parse_timetable_helpers as pt
import handle_bus_data as bus
import matplotlib.pyplot as plt
import utils
import json
import folium
import sys
import load_data as ld
import datetime

(data, stops, routes) = ld.load_data(sys.argv)


sum_percentage_delays = dict()
num_counted_routes = dict()
average_percentage_delays = dict()
bus_numbers = ['105', '106', '136', '186', '523']
for bus_number in bus_numbers:
    all_real_routes = bus.get_all_bus_number_real_routes(stops, routes, data, bus_number)
    for route in all_real_routes:
        buses_in_hours = dict()
        delays_in_hours = dict()
        average_delays = dict()
        for real_route in route:
            time = real_route[int(len(real_route)/2)]['end_time']
            time = utils.convert_time(time)
            hours = time["hours"]
            if hours in buses_in_hours:
                buses_in_hours[hours] += 1
                delays_in_hours[hours] += real_route[-1]['delay']
            else:
                buses_in_hours[hours] = 1
                delays_in_hours[hours] = real_route[-1]['delay']
            route_expected_time = 60 * utils.subtract_time(real_route[-1]['expected_time'], real_route[0]['expected_time'])["hours"] + utils.subtract_time(real_route[-1]['expected_time'], real_route[0]['expected_time'])["minutes"]
        if route_expected_time == 0:
            continue
        for hour in buses_in_hours.keys():
            if hour in delays_in_hours:
                average_delays[hour] = delays_in_hours[hour] / buses_in_hours[hour]
        for hour in buses_in_hours.keys():
            if hour in sum_percentage_delays:
                sum_percentage_delays[hour] += average_delays[hour] / route_expected_time
                num_counted_routes[hour] += 1
            else:
                sum_percentage_delays[hour] = average_delays[hour] / route_expected_time
                num_counted_routes[hour] = 1
for hour in sum_percentage_delays.keys():
    average_percentage_delays[hour] = sum_percentage_delays[hour] / num_counted_routes[hour]

    # Sort the average delays by hour
sorted_delays = sorted(average_percentage_delays.items())

# Extract the hours and delays as separate lists
hours, delays = zip(*sorted_delays)

# Plot the graph as column chart
plt.bar(hours, delays)
plt.xlabel('Hour')
plt.ylabel('Average Delay')
plt.title('Average Delays for Hours')
plt.show()