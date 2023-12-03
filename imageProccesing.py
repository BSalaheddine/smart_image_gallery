from deepface import DeepFace
import os
from PIL import Image
import pandas as pd
import shutil

path = "./static/uploads"
dossiers = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]

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


# dfs = DeepFace.find(img_path = "C:/Users/User/Desktop/image gallery/a.png", db_path = "C:/Users/User/Desktop/image gallery/Faces/Brad Pitt", model_name=models[2])

# print(dfs)


def reconnaissance(img):
  dfs = DeepFace.find(img_path = img, db_path = "./Faces/", model_name=models[2], enforce_detection=False)
  if dfs[0].shape[0] == 0:
    return False