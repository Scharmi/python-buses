import utils

def get_bus_numbers(lines):
    numbers = []
    for line in lines:
        if "Linia" in line:
            number = line.split()[1]
            numbers.append(number)
    return numbers

def get_stop_from_line(line):
    separated_times = line.split("|")
    line = line.split()
    i = 0
    while i < len(line) and not (line[i].isdigit() and len(line[i]) == 6):
        i += 1
    if i == len(line):
        return None
    id = line[i]
    min_time = utils.time_from_minutes(int(separated_times[1].split()[0]))
    max_time = utils.time_from_minutes(int(separated_times[2].split()[0]))
    return {
        "id": id,
        "min_time": min_time,
        "max_time": max_time
    }

def get_route_ids(lines, bus_number, stops):
    possible_stops = stops.keys()
    raw_routes = []
    bus_number_startline_text = "Linia: " + bus_number
    lines = utils.lines_from_until(lines, bus_number_startline_text, "#TR")
    while(utils.lines_from_until(lines, "*LW", "#LW") != []):
        route = utils.lines_from_until(lines, "*LW", "#LW")
        raw_routes.append(route[1:-1])
        lines = utils.delete_lines_until(lines, "#LW")
    routes = []
    for raw_route in raw_routes:
        route = []
        for i in range(len(raw_route)):
            if(get_stop_from_line(raw_route[i]) != None):
                if get_stop_from_line(raw_route[i])['id'] in possible_stops:
                    route.append(get_stop_from_line(raw_route[i]))
        routes.append(route)
    routes.sort(key=len)
    return routes

def get_stops(lines):
    stops = dict()
    lines = utils.lines_from_until(lines, "*ZP", "#ZP")
    name = ""
    for i in range(len(lines)):
        line = lines[i]
        line = line.split()
        if len(line) <= 1 or line is None:
            continue
        if line[0].isdigit() and len(line[0]) == 4:
            name = ""
            j = 1
            while line[j][-1] != "," and line[j] != "--":
                name += line[j] + " "
                j += 1
            if line[j] != "--":
                name += line[j][:-1]
        if line[0].isdigit() and len(line[0]) == 6:
            id = line[0]
            if id == '703702':
                stops[id] = {
                    "name":name,
                    "Lat": '52.218732',
                    "Lon": '21.024556'
                }
                continue
            j = 1
            while "Y=" not in line[j]:
                j += 1
            j += 1
            lat = line[j]
            j += 2
            try:
                lon = line[j]
            except:
                exit(1)
            stop = {
                "name": name,
                "Lat": lat,
                "Lon": lon
            }
            stops[id] = stop
    return stops
def get_routes(id_routes, stops):
    routes = []
    for id_route in id_routes:
        route = []
        for id in id_route:
            for stop in stops:
                if id == stop['id']:
                    route.append(stop)
        routes.append(route)
    return routes

def parse_timetable_for_stop(lines):
    timetable = []
    for line in lines:
        line = line.split()
        if len(line) == 0:
            continue
        if line[0] == "G":
            for i in range(1, len(line)):
                if line[i][-1] == ":":
                    hour = line[i][:-1]
                if line[i][0] == '[':
                    minutes = line[i][1:3]
                    timetable.append({
                        "hours": int(hour),
                        "minutes": int(minutes)
                    })
    return timetable

#Gets timetables for a particular route of a particular bus line
def get_route_timetables(lines, bus_number):
    timetables = []
    #Copy lines
    operation_lines = lines.copy()
    for i in range(len(lines)):
        line = lines[i]
        operation_lines = utils.delete_lines_until(operation_lines, line)
        line = line.split()
        if line[0].isdigit() and len(line[0]) == 6:
            timetables.append({
                "id": line[0],
                "timetable" : parse_timetable_for_stop(utils.lines_from_until(operation_lines, "*WG", "#WG"))
            })
    return timetables

#Gets timetables for all routes of a particular bus line
def get_routes_timetables(lines, bus_number):
    result = []
    bus_number_startline_text = "Linia: " + bus_number
    lines = utils.lines_from_until(lines, bus_number_startline_text, "#TR")
    while(utils.lines_from_until(lines, "*RP", "#RP") != []):
        result.append(get_route_timetables(utils.lines_from_until(lines, "*RP", "#RP"), bus_number))
        lines = utils.delete_lines_until(lines, "#RP")
    return result

