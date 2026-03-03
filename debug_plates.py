#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug script to analyze actual vs expected license plates."""

import os
import cv2
import numpy as np
import pytesseract
from main import preprocess_image, find_all_plates, is_valid_text

# Expected plates for each image
EXPECTED_PLATES = {
    'Képernyőkép 2026-03-03 180009.png': ['AA-AB-301'],
    'Képernyőkép 2026-03-03 180018.png': ['AE-KU-630'],
    'Képernyőkép 2026-03-03 180027.png': ['AA-AA-123'],
    'Képernyőkép 2026-03-03 180041.png': ['AA-KA-266'],
    'Képernyőkép 2026-03-03 180048.png': ['NLE-003', 'NCU-003'],
    'Képernyőkép 2026-03-03 180103.png': ['MO-CKBAZ'],
    'Képernyőkép 2026-03-03 180108.png': ['NLE-682'],
    'Képernyőkép 2026-03-03 180115.png': ['PPZ-461', 'REW-067']
}

SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"

def analyze_image(image_path):
    """Analyze what the OCR finds in an image."""
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        print(f"  ✗ Nem olvasható kép!")
        return
    
    height, width = image.shape[:2]
    edged, gray = preprocess_image(image)
    plate_contours = find_all_plates(edged, width, height)
    
    print(f"  Talált {len(plate_contours)} kontúr")
    
    for idx, plate_cnt in enumerate(plate_contours, 1):
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [plate_cnt], 0, 255, -1)
        (x, y) = np.where(mask == 255)
        (topx, topy) = (np.min(x), np.min(y))
        (bottomx, bottomy) = (np.max(x), np.max(y))
        cropped = gray[topx:bottomx+1, topy:bottomy+1]
        
        # Try different PSM modes
        for psm in [6, 7, 8, 11, 13]:
            config = f"--psm {psm} --oem 3 -c tessedit_char_whitelist={SUPPORTED_CHARS}"
            text = pytesseract.image_to_string(cropped, config=config).strip()
            if text:
                valid = is_valid_text(text)
                print(f"    Kontúr {idx} (PSM {psm}): '{text}' (érvényes: {valid})")

def main():
    base_dir = 'Képek'
    
    for filename in sorted(os.listdir(base_dir)):
        if not filename.endswith('.png'):
            continue
        
        image_path = os.path.join(base_dir, filename)
        expected = EXPECTED_PLATES.get(filename, ['?'])
        
        print(f"\n📷 {filename}")
        print(f"   Elvárt: {expected}")
        analyze_image(image_path)

if __name__ == '__main__':
    main()
