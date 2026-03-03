#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug script to visualize edge detection for each image."""

import os
import cv2
import numpy as np
from main import preprocess_image

base_dir = 'Képek'
output_dir = 'debug_edges'

# Készítsd el az output könyvtárat
os.makedirs(output_dir, exist_ok=True)

for filename in sorted(os.listdir(base_dir)):
    if not filename.endswith('.png'):
        continue
    
    image_path = os.path.join(base_dir, filename)
    print(f"Processing {filename}...")
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        continue
    
    height, width = image.shape[:2]
    edged, gray = preprocess_image(image)
    
    # Kontúrokat rajzold a képre
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # Eredeti kép + zöld kontúrok
    result = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    cv2.drawContours(result, contours, -1, (0, 255, 0), 2)
    
    # Mentsd el
    output_path = os.path.join(output_dir, f"{filename}_edges.png")
    cv2.imwrite(output_path, result)
    
    # Mentsd el az edge detectiont is
    edge_path = os.path.join(output_dir, f"{filename}_canny.png")
    cv2.imwrite(edge_path, edged)
    
    print(f"  Kontúrok: {len(contours)}")
    print(f"  Képek mentve: {output_path}, {edge_path}")

print("\nDebug képek mentve 'debug_edges' mappában!")
