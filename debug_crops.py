#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug: kivágjuk az összes detektált "valid" rendszámtáblát."""

import os
import cv2
import numpy as np
from main import preprocess_image, is_valid_plate

base_dir = 'Képek'
output_dir = 'debug_crops'

os.makedirs(output_dir, exist_ok=True)

for filename in sorted(os.listdir(base_dir)):
    if not filename.endswith('.png'):
        continue
    
    image_path = os.path.join(base_dir, filename)
    print(f"\n{filename}:")
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        continue
    
    height, width = image.shape[:2]
    edged, gray = preprocess_image(image)
    
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_count = 0
    for idx, cnt in enumerate(contours):
        if is_valid_plate(cnt, width, height):
            valid_count += 1
            
            # Bounding rect
            x, y, w, h = cv2.boundingRect(cnt)
            cropped = gray[y:y+h, x:x+w]
            
            # Mentsd el
            crop_path = os.path.join(output_dir, f"{filename[:-4]}_plate_{valid_count}.png")
            cv2.imwrite(crop_path, cropped)
            
            print(f"  Valid kontúr #{valid_count}: Size={w}x{h}, Area={cv2.contourArea(cnt):.0f}, AR={w/h:.2f}")
    
    if valid_count == 0:
        print(f"  NINCS valid kontúr!")

print(f"\n✓ Kivágatott képek mentve: {output_dir}")
