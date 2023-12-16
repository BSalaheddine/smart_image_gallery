from flask import Flask, request, redirect, url_for, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import imageProccesing as imageProccesing
import shutil
import json


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

def get_next_image_number(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            last_image_name = data['name']
            last_number = int(os.path.splitext(last_image_name)[0])
            return last_number + 1
    except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
        return 1

def update_json_file(json_file_path, new_image_name, new_image_path, tag=None):
    try:
        with open(json_file_path, 'r+') as file:
            data = json.load(file)
            if tag:  # If a tag is provided, append it to the tags list for the image
                for image in data:
                    if image['name'] == new_image_name:
                        image['tags'].append(tag)
                        break
            else:  # If no tag, add the new image to the database
                data.append({
                    'name': new_image_name,
                    'path': new_image_path,
                    'tags': []
                })
            file.seek(0)  # Reset file position to the beginning.
            json.dump(data, file, indent=4)
            file.truncate()  # Remove any remaining data from the old content.
    except (FileNotFoundError, json.JSONDecodeError):
        # If the file does not exist or is empty/invalid, create a new list
        data = [{
            'name': new_image_name,
            'path': new_image_path,
            'tags': []
        }]
        with open(json_file_path, 'w') as file:
            json.dump(data, file, indent=4)

@app.route('/', methods=['GET', 'POST'])
def galerie():
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file:
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)

            recognition = imageProccesing.reconnaissance(file_path)

            json_file_path = 'db.json'
            next_image_number = get_next_image_number(json_file_path)
            new_filename = str(next_image_number) + os.path.splitext(filename)[1]
            new_file_path = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)

            if recognition == 0:
                pass
            else:
                recog_path = os.path.dirname(recognition)

            update_json_file(json_file_path, new_filename, new_file_path)
        return redirect('/')

    images = os.listdir(app.config['UPLOAD_FOLDER'])
    images = [os.path.join('static/uploads/', file) for file in images]

    return render_template('galerie.html', images=images)


@app.route('/add-tag', methods=['POST'])
def add_tag():
    tag = request.form['tag']
    image_name = request.form['image']
    json_file_path = 'db.json'
    
    if tag and image_name:
        update_json_file(json_file_path, image_name, None, tag)
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'failure'}), 400

# @app.route('/', methods=['GET', 'POST'])
# def galerie():
#     if request.method == 'POST':
#         image_file = request.files['file']
#         if image_file:
#             filename = secure_filename(image_file.filename)
#             file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
#             image_file.save(file_path)
#             recognition = imageProccesing.reconnaissance(file_path)

#             if recognition == 0:
#                 unique_filename = str(uuid.uuid4()) + os.path.splitext(filename)[1]
#                 unique_folder = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename.split('.')[0])
#                 os.makedirs(unique_folder, exist_ok=True)

#                 shutil.copy(file_path, os.path.join(unique_folder, unique_filename))

#                 return redirect('/')
#             else :
#                 recognition
#                 recog_path= os.path.dirname(recognition)
#                 shutil.copy(file_path, os.path.join(recog_path, unique_filename))

#     images = os.listdir(app.config['UPLOAD_FOLDER'])
#     images = [os.path.join('/static/uploads/', file) for file in images]
#     return render_template('galerie.html', images=images)

@app.route('/submitname', methods=['POST'])
def submit_name():
    name = request.form['name']
    filename = request.form['filename']
    original_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if name and os.path.exists(original_file_path):
        name_folder = os.path.join(app.config['UPLOAD_FOLDER'], name)
        if not os.path.exists(name_folder):
            os.makedirs(name_folder)
        
        new_file_path = os.path.join(name_folder, filename)
        os.rename(original_file_path, new_file_path)
    
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port=5002)
