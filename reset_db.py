import json
import os
with open("db.json", 'w') as json_file:
    json.dump({"images": {},"faces": {},"tags": {"faces": {},"animals": {},"custom_tags": {}}}, json_file, indent=2)

def delete_files_in_directory(directory_path):
    for file_name in os.listdir(directory_path):
        file_path = os.path.join(directory_path, file_name)
        
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
                print(f"Deleted: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

directories = ["static/faces", "static/tmp_image", "static/uploads"]
for directory in directories:
    delete_files_in_directory(directory)