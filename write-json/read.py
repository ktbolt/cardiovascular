
import json

with open('rcrt.json') as json_file:  
    rcr_data = json.load(json_file)

print(">>> desc: ", rcr_data["description"] )
print(">>> max num time: ", rcr_data["MaxNumTimePoints"] )

outlet_data = rcr_data["OutletData"]

for data in outlet_data:
    print(">>> data: ", data) 

