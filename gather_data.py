import json
import requests
import time
import utils
import sys

file_path = './data/' + sys.argv[1] + '.json'
url = "https://api.um.warszawa.pl/api/action/busestrams_get/?resource_id=f2e5503e-927d-4ad3-9500-4ab9e55deb59&type=1&apikey=" + utils.api_key

#Chech if file exists, otherwise create it
try:
    with open(file_path, 'r') as file:
        pass
except:
    with open(file_path, 'w') as file:
        json.dump([], file)
with open(file_path, 'r+') as file:
    try:
        prev_data = json.load(file)
    except:
        prev_data = []
        json.dump(prev_data, file)
while True:
    with open(file_path, 'r+') as file:
        response = requests.get(url)
        data = response.json()
        new_data  = data['result']
        if(type(new_data) == str):
            time.sleep(10)
            #Print error message and continue
            print(new_data)
            continue
        updated_data = new_data + prev_data
        #Overwrite file with new data
        file.seek(0)
        file.truncate()
        json.dump(updated_data, file)
        prev_data = updated_data
        time.sleep(60)
    print("Data updated")

