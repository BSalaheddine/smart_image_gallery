from flask import Flask, request, redirect, url_for, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import imageProccesing
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

def update_json_file(json_file_path, new_image_name, new_image_path):
    new_data = {
        'name': new_image_name,
        'path': new_image_path,
        'tags': []
    }
    with open(json_file_path, 'w') as file:
        json.dump(new_data, file, indent=4)

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
