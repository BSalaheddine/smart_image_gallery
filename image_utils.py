import cv2
from PIL import Image, ImageDraw
import random
import os

def enlarge_area(x, y, w, h, width, height):
    a, b, c, d = max(0,x-w//2), min(width,x+w+w//2), max(0,y-h//2), min(height,y+h+h//2)
    return a, c, b-a, d-c

def crop_face(filepath, face_filepath, x, y, w, h):
    image = cv2.imread(filepath)
    new_x, new_y, new_w, new_h = enlarge_area(x, y, w, h, image.shape[1], image.shape[0])
    cropped_image = image[new_y:new_y+new_h, new_x:new_x+new_w]
    cv2.imwrite(face_filepath, cropped_image)

def add_colored_boxes(filepath, image_data, destination):
    img = Image.open(filepath)

    draw = ImageDraw.Draw(img)

    border_colors = {"faces": [], "animals": []}

    for human in image_data['humans']:
        border_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        border_colors["faces"].append(border_color)

        area = human['area']
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        box_coordinates = [(x, y), (x + w, y + h)]

        draw.rectangle(box_coordinates, outline=border_color, width=2)
    
    for animal in image_data["animals"]:
        border_color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        border_colors["animals"].append(border_color)

        area = animal["area"]
        x, y, w, h = area['x'], area['y'], area['w'], area['h']
        box_coordinates = [(x, y), (x + w, y + h)]

        draw.rectangle(box_coordinates, outline=border_color, width=2)
    
    img.save(destination)
    return border_colors