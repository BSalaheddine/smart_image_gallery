from db import get_db, update_db, add_image_to_db, add_image_to_face, add_face_to_image, add_face_to_db
from deepface import DeepFace
import os
from image_utils import crop_face
import shutil
import uuid

def generate_random_filename(original_filename):
    _, file_extension = os.path.splitext(original_filename)
    random_filename = str(uuid.uuid4()) + file_extension
    return random_filename

def find_faces(filename, filepath, faces_folder):
    data = get_db()
    
    data = add_image_to_db(data, filename)
    
    try:
        faces = DeepFace.extract_faces(filepath, detector_backend="retinaface")
        for face in faces:
            face_filename = generate_random_filename('face.jpg')
            face_path = os.path.join(faces_folder, face_filename)
            
            area = face['facial_area']
            x, y, w, h = area['x'], area['y'], area['w'], area['h']

            crop_face(filepath, face_path, x, y, w, h)

            name = str(uuid.uuid4())
            for file in os.listdir(faces_folder):
                if face_filename != file:
                    result = DeepFace.verify(face_path, os.path.join(faces_folder, file), model_name="Facenet512", detector_backend="retinaface", enforce_detection=False)
                    if result['verified']:
                        name = data['faces'][file]['name']
                        break
                
            data = add_image_to_face(data, name, filename)
            data = add_face_to_image(data, filename, name, area, face_filename)
            data = add_face_to_db(data, face_filename, filename, name)
                    
    except: 
        pass
    
    update_db(data)