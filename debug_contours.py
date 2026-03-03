"""Debug script to check contour detection on problematic image"""

import cv2
import numpy as np
import os
from main import preprocess_image, find_all_plates, is_valid_text
import pytesseract
from pytesseract import pytesseract as pyt_module

path = os.path.abspath(r'Képek\Képernyőkép 2026-03-03 180108.png')
with open(path, 'rb') as f:
    image = cv2.imdecode(np.frombuffer(f.read(), dtype=np.uint8), cv2.IMREAD_COLOR)

height, width = image.shape[:2]
edged, gray = preprocess_image(image)
plate_contours = find_all_plates(edged, width, height)

print(f'Found {len(plate_contours)} plates:')
for idx, cnt in enumerate(plate_contours, 1):
    x, y, w, h = cv2.boundingRect(cnt)
    area = cv2.contourArea(cnt)
    ar = float(w) / h if h > 0 else 0
    print(f'  Plate {idx}: Area={area:.0f}, AR={ar:.2f}, Pos=({x},{y}), Size={w}x{h}')
    
    # Extract and OCR
    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [cnt], 0, 255, -1)
    x_m, y_m = np.where(mask == 255)
    topx, topy = np.min(x_m), np.min(y_m)
    bottomx, bottomy = np.max(x_m), np.max(y_m)
    cropped = gray[topx:bottomx+1, topy:bottomy+1]
    
    config = '--psm 8 --oem 3 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    text = pytesseract.image_to_string(cropped, config=config).strip()
    valid = is_valid_text(text)
    print(f'     Text: "{text}", Valid: {valid}, Len: {len(text)}')
