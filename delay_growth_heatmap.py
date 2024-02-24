import sys
import parse_timetable_helpers as pt
import handle_bus_data as bus
import matplotlib.pyplot as plt
from folium.plugins import HeatMap
import utils
import json
import folium
import load_data as ld
import datetime

(data, stops, routes) = ld.load_data(sys.argv)
#Get all bus numbers
bus_numbers = list(routes.keys())
bus_numbers = bus_numbers[:300]
sum_delays_for_stops = dict()
sum_visitings_for_stops = dict()
average_delays_for_stops = dict()
for bus_number in bus_numbers:
    all_real_routes = bus.get_all_bus_number_real_routes(stops, routes, data, bus_number)
    for route in all_real_routes:
        for real_route in route:
            for i in range(len(real_route) - 1):
                if real_route[i]['id'] in sum_visitings_for_stops:
                    sum_visitings_for_stops[real_route[i]['id']] += 1
                else:
                    sum_visitings_for_stops[real_route[i]['id']] = 1
                if "delay" not in real_route[i].keys() or "delay" not in real_route[i+1].keys():
                    continue
                if(real_route[i+1]['delay'] > real_route[i]['delay']):
                    delay = real_route[i+1]['delay'] - real_route[i]['delay']
                    if real_route[i]['id'] in sum_delays_for_stops:
                        sum_delays_for_stops[real_route[i]['id']] += delay
                    else:
                        sum_delays_for_stops[real_route[i]['id']] = delay

for stop_id in sum_delays_for_stops.keys():
    average_delays_for_stops[stop_id] = sum_delays_for_stops[stop_id] / sum_visitings_for_stops[stop_id]
m = folium.Map(location=[52.22977, 21.01178], zoom_start=12)
max_delay = max(average_delays_for_stops.values())
heat_data = [[stops[stop_id]['Lat'], stops[stop_id]['Lon'], average_delays_for_stops[stop_id] / max_delay] for stop_id in average_delays_for_stops.keys()]
HeatMap(heat_data, radius=40).add_to(m)
m.save('delay_heatmap.html')
