from deepface import DeepFace
import os
from PIL import Image
import pandas as pd
import shutil

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


# dfs = DeepFace.find(img_path = "C:/Users/User/Desktop/image gallery/a.png", db_path = "C:/Users/User/Desktop/smart_image_gallery/Faces", model_name=models[2], enforce_detection=False)

# # print(type(dfs[0]))

# df = dfs[0]

# # print(df.loc[dfs[0][dfs[0]['Facenet512_cosine'] > 0.1]['identity'].first_valid_index(), 'identity'])
# print(len(dfs[0][dfs[0]['Facenet512_cosine'] > 0.4]['identity']))



def reconnaissance(img):
  dfs = DeepFace.find(img_path = img, db_path = "./Faces/", model_name=models[2], enforce_detection=False)
  if len(dfs[0][dfs[0]['Facenet512_cosine'] > 0.4]['identity']) == 0:
    return 0
  else:
    return dfs[0].loc[dfs[0][dfs[0]['Facenet512_cosine'] > 0.4]['identity'].first_valid_index(), 'identity']