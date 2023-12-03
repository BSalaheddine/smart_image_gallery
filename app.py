from flask import Flask, request, redirect, url_for, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import imageProccesing

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads/'

@app.route('/', methods=['GET', 'POST'])
def galerie():
    if request.method == 'POST':
        image_file = request.files['file']
        if image_file:
            filename = secure_filename(image_file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(file_path)
            
            if not imageProccesing.reconnaissance(file_path):
                return jsonify({"requestName": True, "filename": filename})
            else:
                return redirect('/')
    
    images = os.listdir(app.config['UPLOAD_FOLDER'])
    images = [os.path.join('/static/uploads/', file) for file in images]
    return render_template('galerie.html', images=images)

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
    app.run(debug=True, port=25396)
