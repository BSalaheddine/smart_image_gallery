from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import json
import uuid
from deepface import DeepFace
import cv2
from PIL import Image, ImageDraw
import random
import shutil

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
if not os.path.exists(DB_FILE_PATH):
    with open(DB_FILE_PATH, 'w') as json_file:
        json.dump({"images": {},"faces": {},"tags": {"humans": {},"animals": {},"custom_tags": {}}}, json_file)


def add_colored_box(filename, humans_data):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    img = Image.open(file_path)

    # Create a drawing object
    draw = ImageDraw.Draw(img)

    border_colors = []

    for human in humans_data:
        border_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        border_colors.append(border_color)
        area = human['facial_area']
        x, y, w, h = area['x'], area['y'], area['w'], area['h']

        # Define the coordinates of the box
        box_coordinates = [(x, y), (x + w, y + h)]

        # Draw the colored box on the image
        draw.rectangle(box_coordinates, outline=border_color, width=2)

    # Save the modified image to the specified file location
    _, file_extension = os.path.splitext(file_path)
    img.save(os.path.join(app.config['TMP_FOLDER'], "tmp_image")+file_extension)
    return border_colors

def get_image_data(image_filename):
    # Read the existing data from the JSON file
    with open(DB_FILE_PATH, 'r') as json_file:
        data = json.load(json_file)

    # Get data for the specified image
    image_data = data['images'].get(image_filename, {})

    return image_data

def extract_faces(filename):
    # Extract faces
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    # Read json
    with open(DB_FILE_PATH, 'r') as json_file:
        data = json.load(json_file)
    
    # Add file to json
    data['images'][filename] = {
        "humans" : [],
        "animals": [],
        "custom_tags": []
    }
    
    try:
        faces = DeepFace.extract_faces(file_path, detector_backend="retinaface")
        for face in faces:
            face_filename = generate_random_filename('face.jpg')
            tmp_face_path = os.path.join(app.config['TMP_UPLOAD'], face_filename)
            face_path = os.path.join(app.config['FACES_FOLDER'], face_filename)
            
            facial_area = face['facial_area']
            x, y, w, h = facial_area['x'], facial_area['y'], facial_area['w'], facial_area['h']

            # Save cropped face image
            image = cv2.imread(file_path)
            # to crop not too much (makes the recognition model less performant)
            a, b, c, d = max(0,x-w//2), min(image.shape[1],x+w+w//2), max(0,y-h//2), min(image.shape[1],y+h+h//2)
            new_x, new_y, new_w, new_h = a, c, b-a, d-c
            cropped_image = image[new_y:new_y+new_h, new_x:new_x+new_w]
            cv2.imwrite(tmp_face_path, cropped_image)

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
                "facial_area": facial_area,
                "face": face_filename
            })

            # Add face in json
            data['faces'][face_filename] = {
                "from_picture": filename,
                "human": human
            }
    except:
        pass

    # Write json
    with open(DB_FILE_PATH, 'w') as json_file:
        json.dump(data, json_file, indent=2)

def generate_random_filename(original_filename):
    _, file_extension = os.path.splitext(original_filename)
    random_filename = str(uuid.uuid4()) + file_extension
    return random_filename

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

        return redirect(url_for('index'))
    
@app.route('/image/<image_filename>')
def display_image(image_filename):
    # Get data for the specified image
    image_data = get_image_data(image_filename)

    border_colors = add_colored_box(image_filename, image_data['humans'])

    # Render the image display template
    _, file_extension = os.path.splitext(image_filename)
    displayed_image = "tmp_image" + file_extension
    return render_template('image.html', displayed_image = displayed_image, image_filename=image_filename, image_data=image_data, border_colors=border_colors)

if __name__ == '__main__':
    app.run(debug=True)
