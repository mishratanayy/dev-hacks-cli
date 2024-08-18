import json
import urllib
import os
#project = https://qa-demo-24-1.dev.bb.schrodinger.com/livedesign/#/projects/1351/livereports/125310
url = "https://qa-demo-24-1.dev.bb.schrodinger.com/"
# live_report_id = "125310"
live_report_id = "112876"
# column_ids = ["6","17981"]
column_ids = [
    "53787", "17633", "16433", "138459", "18813", "6", "6643", "157489",
    "152584", "22082", "5691", "19516", "167231", "43007", "157484"
]
# row_keys = ["CMPD-10392","CMPD-10402","CMPD-10428"]
row_keys = ["CMPD-10460"]
report_level = "parent"


def print_json():
    json_dict = {}
    json_dict['url'] = url
    json_dict['live_report_id'] = live_report_id
    json_dict['column_ids'] = column_ids
    json_dict['row_keys'] = row_keys
    json_dict['report_level'] = report_level
    json_dict['user'] = "testadmin"
    json_dict['action'] = "import_structure"
    json_object = json.dumps(json_dict)
    print(json_object)
    print("\n")
    uri_encoded = urllib.parse.quote(json_object)
    final_request = f"maestro://{uri_encoded}"
    SCHRODINGER = os.getenv("SCHRODINGER")
    CMDS = [f"{SCHRODINGER}/maestro", "-console", "-o", final_request]
    print(" ".join(CMDS))


def get_request():
    json_string = '{"live_report_id":"98607","report_level":"parent","column_ids":["53787","114544","17633","138459","139346","18813","6","17981","158140","6643","22082","114190","114189","151779","63890","5691","19516","43007","150904","150902","160751","114779","117779","118432"],"row_keys":["V47530"]}'
    json_object = json.loads(json_string)
    json_object["user"] = "testuser1"
    json_object["url"] = url
    json_object["report_level"] = "parent"
    print(json_object)
    json_string = json.dumps(json_object)
    uri_encoded = urllib.parse.quote(json_string)
    final_request = f"maestro://{uri_encoded}"
    SCHRODINGER = os.getenv("SCHRODINGER")
    CMDS = [f"{SCHRODINGER}/maestro", "-console", "-o", final_request]
    print(" ".join(CMDS))


def get_arguments():
    json_request = "%7B%22action%22%3A%22import_structure%22%2C%22url%22%3A%22https%3A%2F%2Fqa-demo-24-2.dev.bb.schrodinger.com%2F%22%2C%22live_report_id%22%3A%22102962%22%2C%22report_level%22%3A%22pose%22%2C%22column_ids%22%3A%5B%2218592%22%5D%2C%22row_keys%22%3A%5B%22V51973-87493084%22%5D%2C%22user%22%3A%22testuser1%22%7D"
    url_decode = urllib.parse.unquote(json_request)
    print(url_decode)
    #json_object = json.loads(url_decode)
    #print(json_object)


if __name__ == '__main__':

    print_json()

    print("\n\n\n")
    get_request()

    print("\n\n\n")
    get_arguments()
