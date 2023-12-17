from PIL import Image
from ultralytics import YOLO

# Load YOLO model
model = YOLO('best.pt')

def reconnnaissance_animal(img_path, confidence_threshold=0.0):
    try:
        # Load the image
        img = Image.open(img_path).convert("RGB")

        # Make predictions using the YOLO model
        results = model(img)

        # Collect the coordinates and names of the detected boxes
        detections = []
        for r in results:
            if r is not None and r.names is not None and r.boxes is not None:
                classes = list(r.boxes.cls)
                classes_names = []
                for elem in classes :
                    element = elem.tolist()
                    classes_names.append(r.names[element])
                boxes = r.boxes.xyxy if hasattr(r.boxes, 'xyxy') else r.boxes  # Try accessing 'xyxy', fallback to 'boxes'
                for box in boxes:
                    print("Box:", box)
                    detections.append(box)
                # im_array = r.plot()
                # im = Image.fromarray(im_array[..., ::-1])  # Convert BGR to RGB
                # im.show()  # Show the image
                # im.save('results.jpg')  # Save the image

            formatted_coordinates = []

            for coord in detections:
                x, y, x_max, y_max = coord.tolist()
                w = x_max - x
                h = y_max - y
                formatted_coordinates.append({'x': x, 'y': y, 'w': w, 'h': h})
        return formatted_coordinates,classes_names

    except Exception as e:
        print(f"Error processing image: {e}")
        return []


