import cv2
import os

def enlarge_area(x, y, w, h, width, height):
    a, b, c, d = max(0,x-w//2), min(width,x+w+w//2), max(0,y-h//2), min(height,y+h+h//2)
    return a, c, b-a, d-c

def crop_face(filepath, face_filepath, x, y, w, h):
    image = cv2.imread(filepath)
    new_x, new_y, new_w, new_h = enlarge_area(x, y, w, h, image.shape[1], image.shape[0])
    cropped_image = image[new_y:new_y+new_h, new_x:new_x+new_w]
    cv2.imwrite(face_filepath, cropped_image)