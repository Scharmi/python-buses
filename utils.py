import geopy
from datetime import datetime
api_key = "6d2d6b9f-5ab6-471f-8abc-d389e007d22b"

def distance_in_kilometers(lat1, lon1, lat2, lon2):
    from geopy.distance import geodesic
    coords_1 = (lat1, lon1)
    coords_2 = (lat2, lon2)
    return geodesic(coords_1, coords_2).kilometers


def get_buses_by_line(line, data):
    buses = []
    for bus in data:
        if bus['Lines'] == line:
            buses.append(bus)
    return buses

def time_difference_in_hours(time1, time2):
    if(type(time1) == str):
        time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
    if(type(time2) == str):
        time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
    return (time2 - time1).seconds / 3600

def average_time(time1, time2):
    from datetime import datetime
    time1 = datetime.strptime(time1, '%Y-%m-%d %H:%M:%S')
    time2 = datetime.strptime(time2, '%Y-%m-%d %H:%M:%S')
    return time1 + (time2 - time1) / 2

def windows_1250_to_utf8(text):
    return text.encode('windows-1250').decode('utf-8')

def lines_from_until(lines, start_subword, end_subword):
    start_index = next((i for i, line in enumerate(lines) if start_subword in line), None)
    if start_index is None:
        return []
    for i in range(start_index, len(lines)):
        if end_subword in lines[i]:
            end_index = i + 1
            break
    return lines[start_index:end_index]

def delete_lines_until(lines, subword):
    start_index = next((i for i, line in enumerate(lines) if subword in line), None)
    if start_index is not None:
        del lines[:start_index + 1]
    return lines

def any_line_contains(lines, subword):
    for line in lines:
        if subword in line:
            return True
    return False

def add_time(time_1, tim_2):
    hours = time_1['hours'] + tim_2['hours']
    minutes = time_1['minutes'] + tim_2['minutes']
    if minutes >= 60:
        hours += 1
        minutes -= 60
    if minutes < 0:
        hours -= 1
        minutes += 60
    hours = hours % 24
    return {'hours': hours, 'minutes': minutes}

def subtract_time(time_1, time_2):
    hours = time_1['hours'] - time_2['hours']
    minutes = time_1['minutes'] - time_2['minutes']
    if minutes >= 60:
        hours += 1
        minutes -= 60
    if minutes < 0:
        hours -= 1
        minutes += 60
    hours = hours % 24
    return {'hours': hours, 'minutes': minutes}

def time_greater_equal_than(time_1, time_2):
    if time_1['hours'] > time_2['hours']:
        return True
    if time_1['hours'] == time_2['hours'] and time_1['minutes'] >= time_2['minutes']:
        return True
    return False
def time_is_between(time, start, end):
    if time_greater_equal_than(start, end):
        return time_greater_equal_than(time, start) and time_greater_equal_than(end, time)
    return time_greater_equal_than(time, start) and time_greater_equal_than(end, time)

def time_from_minutes(minutes):
    hours = minutes // 60
    minutes = minutes % 60
    return {'hours': hours, 'minutes': minutes}

def convert_time(time):
    if(type(time) == str):
        hours = int(time[11:13])
        minutes = int(time[14:16])
        return {
            "hours": hours,
            "minutes": minutes
        }
    return {
        "hours": time.hour,
        "minutes": time.minute
    }

def convert_to_datetime(time):
    if(type(time) == str):
        return datetime.strptime(time, '%Y-%m-%d %H:%M:%S')
    return time