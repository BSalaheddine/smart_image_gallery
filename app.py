from flask import Flask, render_template, request, redirect, url_for
import os
from flask import request
from animals import find_animals
from db import create_db, get_db, update_db, add_custom_tag_to_image, replace_in_db, get_all_tags, remove_custom_tag, remove_custom_tag_from_image
from image_utils import add_colored_boxes
from faces import find_faces, generate_random_filename


app = Flask(__name__)

# Initialize folders
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['FACES_FOLDER'] = os.path.join('static', 'faces')
app.config['TMP_FOLDER'] = os.path.join('static', 'tmp_image')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['FACES_FOLDER'], exist_ok=True)
os.makedirs(app.config['TMP_FOLDER'], exist_ok=True)

create_db()

@app.route('/')
def index():
    image_files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]

    page = request.args.get('page', 1, type=int)
    items_per_page = 20  # 5 columns * 4 rows
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_files = image_files[start:end]
    number_of_pages = (len(image_files) - 1) // 20 + 1

    all_labels = get_all_tags()

    return render_template('index.html', image_files=paginated_files, page=page, number_of_pages=number_of_pages, all_labels=all_labels)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']

    if file.filename == '':
        return redirect(request.url)

    if file:
        random_filename = generate_random_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], random_filename)
        file.save(file_path)

        find_faces(random_filename, file_path, app.config['FACES_FOLDER'])
        find_animals(random_filename, file_path)

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

    return render_template('image.html', tmp_file_path=tmp_file_path, filename=filename, image_data=image_data, border_colors=border_colors, displayed_image=displayed_image)

# ...

@app.route('/filter/<label>')
def filter_by_label(label):
    data = get_db()
    if label in data['tags']['faces']:
        filtered_images = data['tags']['faces'][label]
    elif label in data['tags']['animals']:
        filtered_images = data['tags']['animals'][label]
    elif label in data['tags']['custom_tags']:
        filtered_images = data['tags']['custom_tags'][label]

    page = request.args.get('page', 1, type=int)
    items_per_page = 20  # 5 columns * 4 rows
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_files = filtered_images[start:end]

    page = request.args.get('page', 1, type=int)
    items_per_page = 20  # 5 columns * 4 rows
    start = (page - 1) * items_per_page
    end = start + items_per_page
    paginated_files = filtered_images[start:end]
    number_of_pages = (len(filtered_images) - 1) // items_per_page + 1

    all_labels = get_all_tags()

    return render_template('filtered_images.html', image_files=paginated_files, label=label, page=page, number_of_pages=number_of_pages, all_labels=all_labels)

@app.route('/add_custom_label/<image_filename>', methods=['POST'])
def add_custom_label(image_filename):
    custom_label = request.form.get('custom_label')

    if custom_label:
        data = get_db()

        add_custom_tag_to_image(data, image_filename, custom_label)

        update_db(data)

    return redirect(url_for('display_image', filename=image_filename))

@app.route('/rename_tag/<label>', methods=['POST'])
def rename_tag(label):
    new_tag_name = request.form.get('new_tag_name')

    if new_tag_name:
        replace_in_db(label, new_tag_name)

    return redirect(url_for('filter_by_label', label=new_tag_name))

@app.route('/delete_tag/<label>', methods=['POST'])
def delete_tag(label):
    data = get_db()
    remove_custom_tag(data, label)
    update_db(data)
    return redirect(url_for('index'))

@app.route('/remove_tag/<image>', methods=['POST'])
def remove_tag(image):
    label = request.args.get('label', type=str)
    data = get_db()
    remove_custom_tag_from_image(data, image, label)
    update_db(data)
    return redirect(url_for('display_image', filename=image))

if __name__ == '__main__':
    app.run(debug=True)