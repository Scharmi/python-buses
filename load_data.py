import json

def load_data(argv):
    with open("data/routes.json", "r") as file:
        routes = json.load(file)
    with open("data/stops.json", "r") as file:
        stops = json.load(file)
    data = []
    for i in range(1,len(argv)):
        with open("data/" + argv[i] + ".json", "r") as file:
            current_data = json.load(file)
        data = data + current_data
    for record in data:
        if(type(record['Time']) != str):
            record['Time'] = record['Time'].strftime("%Y-%m-%d %H:%M:%S")
    data = [record for record in data if record['Lines'] in routes.keys()]
    return data, stops, routes