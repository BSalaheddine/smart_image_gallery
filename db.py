import json
import os

DB_FILE_PATH = 'db.json'

def create_db():
    if not os.path.exists(DB_FILE_PATH):
        data = {"images": {},"faces": {},"tags": {"humans": {},"animals": {},"custom_tags": {}}}
        update_db(data)

def get_db():
    # Read the existing data from the JSON file
    with open(DB_FILE_PATH, 'r') as json_file:
        data = json.load(json_file)
    return data

def add_image_to_db(data, filename):
    data['images'][filename] = {
        "humans" : [],
        "animals": [],
        "custom_tags": []
    }
    return data

def add_image_to_species(data, species, image):
    if species in data["tags"]["animals"] : 
        data['tags']['animals'][species].append(image)
    else : 
        data['tags']['animals'][species] = [image]
    return data

def add_animal_to_image(data, image, species, area):
    data['images'][image]["animals"].append({
        "species": species,
        "area": area
        })
    return data

def update_db(data):
    with open(DB_FILE_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=2)