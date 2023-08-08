import json
import urllib

session_id = ""
url = "https://qa-demo-23-2.dev.bb.schrodinger.com"
attachment_ids = [
    "64044694-36cd-4b2a-b028-da1137257dc1",
    "64044694-36cd-4b2a-b028-da1137257dc1"
]


def print_json():
    json_dict = {}
    json_dict['session_id'] = session_id
    json_dict['url'] = url
    json_dict['attachment_ids'] = attachment_ids
    json_object = json.dumps(json_dict)
    uri_encoded = urllib.parse.quote(json_object)
    final_request = f"maestro://{uri_encoded}"
    print(final_request)


if __name__ == '__main__':
    print_json()
