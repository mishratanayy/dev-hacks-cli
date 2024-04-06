import json
import urllib
import os

url = "https://qa-demo-24-2.dev.bb.schrodinger.com"
live_report_id = "118269"
column_ids = ["18592","6"]
row_keys = ["CMPD-13670","CMPD-13670"]
report_level = "parent"

def print_json():
    json_dict = {}
    json_dict['url'] = url
    json_dict['live_report_id'] = live_report_id
    json_dict['column_ids'] = column_ids
    json_dict['row_keys'] = row_keys
    json_dict['report_level'] = report_level
    json_dict['user'] = "testuser1"
    json_object = json.dumps(json_dict)
    uri_encoded = urllib.parse.quote(json_object)
    final_request = f"maestro://{uri_encoded}"
    SCHRODINGER = os.getenv("SCHRODINGER")
    CMDS = [f"{SCHRODINGER}/maestro", "-console","-o",final_request]
    print(" ".join(CMDS))



if __name__ == '__main__':
    print_json()
