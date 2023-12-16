import json
with open("db.json", 'w') as json_file:
    json.dump({"images": {},"faces": {},"tags": {"humans": {},"animals": {},"custom_tags": {}}}, json_file)