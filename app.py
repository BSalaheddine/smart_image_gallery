from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import uuid
from deepface import DeepFace
from PIL import Image, ImageDraw
import random
import shutil
from flask import request
from PIL import Image
from ultralytics import YOLO
from animals import reconnnaissance_animal
from db import create_db, get_db, add_image_to_db, update_db
from image_utils import crop_face, add_colored_boxes


# Load a pretrained YOLOv8n model
model = YOLO('best.pt')

app = Flask(__name__)

# Initialize folders
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['FACES_FOLDER'] = os.path.join('static', 'faces')
app.config['TMP_FOLDER'] = os.path.join('static', 'tmp_image')
app.config['TMP_UPLOAD'] = os.path.join('static', 'tmp_upload')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FACES_FOLDER'], exist_ok=True)
os.makedirs(app.config['TMP_FOLDER'], exist_ok=True)
os.makedirs(app.config['TMP_UPLOAD'], exist_ok=True)

# Initialize json
DB_FILE_PATH = 'db.json'

create_db()

def extract_faces(filename):
    # Extract faces
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    data = get_db()
    
    data = add_image_to_db(data, filename)
    
    try:
        faces = DeepFace.extract_faces(file_path, detector_backend="retinaface")
        for face in faces:
            face_filename = generate_random_filename('face.jpg')
            tmp_face_path = os.path.join(app.config['TMP_UPLOAD'], face_filename)
            face_path = os.path.join(app.config['FACES_FOLDER'], face_filename)
            
            area = face['facial_area']
            x, y, w, h = area['x'], area['y'], area['w'], area['h']

            crop_face(file_path, tmp_face_path, x, y, w, h)

            found = False
            for file in os.listdir(app.config['FACES_FOLDER']):
                result = DeepFace.verify(tmp_face_path, os.path.join(app.config['FACES_FOLDER'], file), model_name="Facenet512", detector_backend="retinaface", enforce_detection=False)
                if result['verified']:
                    found = True
                    other_face = file
                    break
            
            shutil.move(tmp_face_path, face_path)
            
            if found:
                human = data['faces'][other_face]['human']
                # Add face to existing tag in json
                data['tags']['humans'][human].append(filename)
            else:
                human = str(uuid.uuid4())
                # Add new tag in json
                data['tags']['humans'][human] = [filename]
                

            # Add face to image in json
            data['images'][filename]["humans"].append({
                "name": human,
                "area": area,
                "face": face_filename
            })

            # Add face in json
            data['faces'][face_filename] = {
                "from_picture": filename,
                "human": human
            }
            
                    
    except: 
        pass

    # Reconnaitre l'animal
    # Save l'image qq part
    # Get la race 
    # Save dans les tags du json
    # Supperposer les 2 images
    
    
    update_db(data)

def generate_random_filename(original_filename):
    _, file_extension = os.path.splitext(original_filename)
    random_filename = str(uuid.uuid4()) + file_extension
    return random_filename

def animals(filename) :

    data = get_db()

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    boxes,classes = reconnnaissance_animal(file_path)
    if (len(boxes) > 0) :
        for box,race in zip(boxes,classes) : 
            # Bow = {'x': x, 'y': y, 'w': w, 'h': h} 
            # race = juste un string
            # ajouter le cadre à l'image
            # ajouter tag par tag au json
            data['images'][filename]["animals"].append({
            "race": race,
            "area": box ,
            })
            #vérifier si le tag existe
            found = False
            if race in data["tags"]["animals"] : 
                data['tags']['animals'][race].append(filename)
            else : 
                data['tags']['animals'][race] = [filename]

    update_db(data)
    

@app.route('/')
def index():
    # Get a list of uploaded image files
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    # Pagination logic
    page = request.args.get('page', 1, type=int)
    items_per_page = 40  # 8 columns * 5 rows
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_files = image_files[start:end]

    return render_template('index.html', image_files=paginated_files, page=page)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        # Generate a random filename to avoid duplicates
        random_filename = generate_random_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)

        # Save the uploaded file with the random filename
        file.save(file_path)

        # Update the JSON database with information about the new file and face
        extract_faces(random_filename)
        animals(filename=random_filename)
        return redirect(url_for('index'))
    
@app.route('/image/<filename>')
def display_image(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    _, file_extension = os.path.splitext(filename)
    tmp_file_path = os.path.join(app.config['TMP_FOLDER'], "tmp_image")+file_extension
    displayed_image = "tmp_image" + file_extension

    print(tmp_file_path)

    data = get_db()
    image_data = data['images'][filename]

    border_colors = add_colored_boxes(file_path, image_data, tmp_file_path)

    return render_template('image.html', tmp_file_path=tmp_file_path, image_filename=filename, image_data=image_data, border_colors=border_colors, displayed_image=displayed_image)

# ...

@app.route('/filter/<label>')
def filter_by_label(label):
    # Get a list of images with the specified label
    data = get_db()
    if label in data['tags']['humans']:
        filtered_images = data['tags']['humans'][label]
    elif label in data['tags']['animals']:
        filtered_images = data['tags']['animals'][label]
    elif label in data['tags']['custom_tags']:
        filtered_images = data['tags']['custom_tags'][label]

    # Pagination logic (you can adjust this based on your needs)
    page = request.args.get('page', 1, type=int)
    items_per_page = 40  # 8 columns * 5 rows
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_files = filtered_images[start:end]

    # Calculate total pages
    total_pages = (len(filtered_images) + items_per_page - 1) // items_per_page

    return render_template('filtered_images.html', image_files=paginated_files, label=label, page=page, total_pages=total_pages)

@app.route('/add_custom_label/<image_filename>', methods=['POST'])
def add_custom_label(image_filename):
    custom_label = request.form.get('custom_label')

    # Ensure the custom label is not empty
    if custom_label:
        # Get existing data from the JSON file
        data = get_db()

        # Check if the image exists in the database
        if image_filename in data['images']:
            # Add the custom label to the image's custom_tags
            data['images'][image_filename]['custom_tags'].append(custom_label)

            # Add the custom label to the overall custom_tags in tags
            data['tags']['custom_tags'].setdefault(custom_label, []).append(image_filename)

            update_db(data)

    # Redirect back to the image details page
    return redirect(url_for('display_image', image_filename=image_filename))

@app.route('/rename_tag/<label>', methods=['POST'])
def rename_tag(label):
    new_tag_name = request.form.get('new_tag_name')

    # Ensure the new tag name is not empty
    if new_tag_name:

        with open(DB_FILE_PATH, 'r') as file:
            content = file.read()
            modified_content = content.replace(label, new_tag_name)
        
        with open(DB_FILE_PATH, 'w') as file:
            file.write(modified_content)

    # Redirect back to the filtered images page
    return redirect(url_for('filter_by_label', label=new_tag_name))

if __name__ == '__main__':
    app.run(debug=True)
