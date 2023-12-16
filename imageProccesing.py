from deepface import DeepFace
import os
from PIL import Image
import pandas as pd
from retinaface import RetinaFace
import matplotlib.pyplot as plt

# path = "./uploads"
# dossiers = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

models = [
  "VGG-Face", 
  "Facenet", 
  "Facenet512", 
  "OpenFace", 
  "DeepFace", 
  "DeepID", 
  "ArcFace", 
  "Dlib", 
  "SFace",
]


# dfs = DeepFace.find(img_path = "C:/Users/User/Desktop/smart_image_gallery/elon2.png", db_path = "C:/Users/User/Desktop/smart_image_gallery/static", model_name=models[2], enforce_detection=False, detector_backend="retinaface")

# print(dfs, dfs[0].loc[dfs[0][dfs[0]['Facenet512_cosine'] > 0]['identity'].first_valid_index(), 'identity'])

# df = dfs[0]

# print(df.loc[dfs[0][dfs[0]['Facenet512_cosine'] > 0.1]['identity'].first_valid_index(), 'identity'])
# print(len(dfs[0][dfs[0]['Facenet512_cosine'] > 0.4]['identity']))



def reconnaissance(img):
  dfs = DeepFace.find(img_path = img, db_path = "./Faces/", model_name=models[2], enforce_detection=False)
  if len(dfs[0][dfs[0]['Facenet512_cosine'] > 0.4]['identity']) == 0:
    return 0
  else:
    return dfs[0].loc[dfs[0][dfs[0]['Facenet512_cosine'] > 0.4]['identity'].first_valid_index(), 'identity']
  

# resp = RetinaFace.detect_faces(img_path=)
# print(resp)

# embedding_objs = DeepFace.extract_faces(img_path = "elon2.png",detector_backend="retinaface")

# if embedding_objs:
#     # Iterate through the list of extracted faces
#     for i, face_dict in enumerate(embedding_objs):
#         # Extract the face image
#         face_image = face_dict['face']

#         # Define the file name for the extracted face
#         face_file_name = os.path.join("Faces", f"face_{i+1}.png")

#         # Save the face image
#         plt.imsave(face_file_name, face_image)

#         print(f"Face {i+1} saved as {face_file_name}")
# else:
#     print("No faces detected.")