import json
import os

DB_FILE_PATH = 'db.json'

def create_db():
    if not os.path.exists(DB_FILE_PATH):
        data = {"images": {},"faces": {},"tags": {"faces": {},"animals": {},"custom_tags": {}}}
        update_db(data)

def get_db():
    # Read the existing data from the JSON file
    with open(DB_FILE_PATH, 'r') as json_file:
        data = json.load(json_file)
    return data

def get_all_tags():
    data = get_db()
    return list(data['tags']['faces']) + list(data['tags']['animals']) + list(data['tags']['custom_tags'])

def add_image_to_db(data, filename):
    data['images'][filename] = {
        "faces" : [],
        "animals": [],
        "custom_tags": []
    }
    return data

def add_face_to_db(data, face_filename, filename, name):
    data['faces'][face_filename] = {
        "from_picture": filename,
        "name": name
    }
    return data

def add_image_to_species(data, species, image):
    if species in data['tags']['animals'] : 
        data['tags']['animals'][species].append(image)
    else : 
        data['tags']['animals'][species] = [image]
    return data

def add_image_to_face(data, face, image):
    if face in data['tags']['faces']:
        data['tags']['faces'][face].append(image)
    else:
        data['tags']['faces'][face] = [image]
    return data

def add_animal_to_image(data, image, species, area):
    data['images'][image]["animals"].append({
        "species": species,
        "area": area
        })
    return data

def add_face_to_image(data, image, name, area, face_filename):
    data['images'][image]["faces"].append({
        "name": name,
        "area": area,
        "face": face_filename
        })
    return data

def add_custom_tag_to_image(data, image, custom_tag):
    if custom_tag in data['tags']['custom_tags']:
        data['tags']['custom_tags'][custom_tag].append(image)
    else:
        data['tags']['custom_tags'][custom_tag] = [image]
    data['images'][image]['custom_tags'].append(custom_tag)
    return data

def update_db(data):
    with open(DB_FILE_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=2)

def replace_in_db(search, replace):
    with open(DB_FILE_PATH, 'r') as file:
        content = file.read()
        modified_content = content.replace(search, replace)
    
    with open(DB_FILE_PATH, 'w') as file:
        file.write(modified_content)