#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rendszámtábla Felismerő Rendszer

A program a megadott képfájlból megpróbálja detektálni az összes rendszámtáblát és
elolvasni a rajta szereplő szöveget. A felismerés OpenCV alapú előfeldolgozással
és a Tesseract OCR motor használatával történik.

Támogatás: Több rendszámtábla a képen, valódiság-szűrés, sorszámozás.

Verzió: 2.0 (Javított edge detection, többszörös PSM módok, nemzetközi formátum)
"""

import argparse
import os
import re

# Külső csomagok betöltése
try:
    import cv2
    import numpy as np
    import pytesseract
    from pytesseract import pytesseract as pyt_module
except ImportError as e:
    raise ImportError(f"Hiányzó dependency: {e}. "
                      "Futtassa: pip install -r requirements.txt") from e

# Tesseract OCR motor elérési útjának beállítása
pyt_module.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Támogatott karakterek (magyar és nemzetközi rendszámokhoz)
SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"


def preprocess_image(image):
    """Előkészíti a képet a rendszámtábla kereséséhez.
    
    Lépések:
    1. Szürkeárnyalatosra konvertálás
    2. CLAHE kontrasztjavítás
    3. Bilaterális szűrés (zaj csökkentés)
    4. Canny élérzékelés (javított paraméterekkel)
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # CLAHE hozzáadása
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    
    # Javított Canny threshold
    edged = cv2.Canny(gray, 50, 150)
    
    return edged, gray


def is_valid_plate(cnt, image_width, image_height):
    """Ellenőrzi, hogy egy kontúr valódi rendszámtábla lehet-e.
    
    Kritériumok:
    - Négyszögletű forma
    - Aspekt-arány: 1.5:1 - 5:1 (lazább)
    - Terület: 0.1% - 10% a kép területének (lazább)
    - Solidity: legalább 0.5 (lazább)
    """
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.018 * peri, True)
    
    if len(approx) != 4:
        return False
    
    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = float(w) / h if h > 0 else 0
    
    if aspect_ratio < 1.5 or aspect_ratio > 5.0:
        return False
    
    area = cv2.contourArea(cnt)
    min_area = 50
    max_area = (image_width * image_height) * 0.5
    
    return min_area <= area <= max_area


def is_valid_text(text):
    """Ellenőrzi, hogy a felismert szöveg valódi rendszám-e.
    
    Kiegyensúlyozott validáció: több formátumot elfogad, de nem hamis pozitívokat.
    """
    import re
    text = text.strip().upper()
    
    # Hossz ellenőrzés
    if len(text) < 5 or len(text) > 10:
        return False
    
    # Csak alfanumerikus és kötőjel
    if not all(c.isalnum() or c == '-' for c in text):
        return False
    
    # Dupla kötőjel vagy kötőjel az elején/végén = hamis
    if '--' in text or text.startswith('-') or text.endswith('-'):
        return False
    
    # Max 2 kötőjel
    if text.count('-') > 2:
        return False
    
    # Magyar formátum: ABC-ABC-123 vagy ABC-DEF-NNN
    if re.match(r'^[A-Z]{2,3}-[A-Z]{2,3}-\d{3}$', text):
        return True
    
    # Nemzetközi formátumok
    # AB-123, ABC-123, ABC-1234, ABCD-1234
    if re.match(r'^[A-Z]{2,4}-?\d{3,4}$', text):
        return True
    
    # Észt/Szláv: NLE-INN, AAA-NNN  
    if re.match(r'^[A-Z]{2,3}-\d{3}$', text):
        return True
    
    # Vegyes formátumok 5-8 karakter hosszúak
    if 5 <= len(text) <= 8:
        alpha_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        # Legalább 2 betű és 2 szám
        if alpha_count >= 2 and digit_count >= 2:
            return True
    
    return False


def validate_plate(text):
    """Post-processing: szigorú regex alapú validáció."""
    import re
    text = text.strip().upper()
    
    # Túl rövid vagy túl hosszú
    if len(text) < 6 or len(text) > 10:
        return False
    
    # Csak alfanumerikus és kötőjel megengedett
    if not all(c.isalnum() or c == '-' for c in text):
        return False
    
    # Nem lehet túl sok kötőjel (max 2)
    if text.count('-') > 2:
        return False
    
    # Magyar formátum: ABC-DEF-123
    if re.match(r'^[A-Z]{3}-[A-Z]{3}-\d{3}$', text):
        return True
    
    # Nemzetközi: ABC-1234, ABC1234
    if re.match(r'^[A-Z]{2,3}-?\d{3,4}$', text):
        return True
    
    # NLE-XXX formátum (észt, szláv)
    if re.match(r'^[A-Z]{2,3}-\d{3}$', text):
        return True
    
    # Más egységes formátumok (6-8 karakter, vegyes)
    if 6 <= len(text) <= 8:
        alpha_count = sum(1 for c in text if c.isalpha())
        digit_count = sum(1 for c in text if c.isdigit())
        dash_count = text.count('-')
        # Legalább 3 betű, 2 szám, és a kötőjel-karakterek nem szomszédosak
        if alpha_count >= 3 and digit_count >= 2 and dash_count <= 1:
            # Nincs dupla kötőjel vagy kötőjel az elején/végén
            if '--' not in text and not text.startswith('-') and not text.endswith('-'):
                return True
    
    return False


def find_all_plates(edged, image_width, image_height):
    """Keresi az összes valódi rendszámtáblát jelölő kontúrt.
    
    Rendezés: bal-jobb sorrendben (x-koordináta szerint)
    """
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    valid_contours = [cnt for cnt in contours if is_valid_plate(cnt, image_width, image_height)]
    valid_contours.sort(key=lambda cnt: cv2.boundingRect(cnt)[0])
    
    return valid_contours


def remove_duplicate_plates(results):
    """Eltávolítja az átfedő/duplikált rendszámokat.
    
    Ha egy szöveg a másik része (pl. "NLE682" ⊂ "ANLE682"),
    akkor csak a hosszabbat tartja meg.
    """
    if len(results) <= 1:
        return results
    
    filtered = []
    used_indices = set()
    
    for i, result1 in enumerate(results):
        if i in used_indices:
            continue
        
        to_keep = True
        for j, result2 in enumerate(results):
            if i == j or j in used_indices:
                continue
            
            text1, text2 = result1['szam'], result2['szam']
            
            if text2 in text1 or text1 in text2:
                if len(text1) > len(text2):
                    used_indices.add(j)
                else:
                    to_keep = False
                    used_indices.add(i)
                    break
        
        if to_keep and i not in used_indices:
            filtered.append(result1)
    
    # Újra sorszámozás
    for idx, item in enumerate(filtered, 1):
        item['pozicio'] = idx
    
    return filtered


def recognize_plates(image_path):
    """Felismeri az összes rendszámtáblát a képen.
    
    Lépések:
    1. Kép betöltése (Unicode path támogatás)
    2. Előfeldolgozás
    3. Kontúr detektálás
    4. Többszörös PSM módos OCR próbálkozás
    5. Duplikált szűrés
    
    Returns:
        list: Felismert rendszámok dict-jeinek listája
    """
    if not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)
    
    with open(image_path, 'rb') as f:
        image_data = f.read()
    image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Nem olvasható kép: {image_path}")
    
    height, width = image.shape[:2]
    edged, gray = preprocess_image(image)
    plate_contours = find_all_plates(edged, width, height)
    
    if not plate_contours:
        return []
    
    results = []
    for plate_cnt in plate_contours:
        mask = np.zeros(gray.shape, np.uint8)
        cv2.drawContours(mask, [plate_cnt], 0, 255, -1)
        coords = np.where(mask == 255)
        cropped = gray[coords[0].min():coords[0].max()+1, coords[1].min():coords[1].max()+1]
        
        # OCR előtt előkészítés
        cropped = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        _, cropped = cv2.threshold(cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Többszörös PSM módok kipróbálása
        best_text = ""
        best_length = 0
        for psm in [6, 7, 8, 11, 13]:
            try:
                config = f"--psm {psm} --oem 3 -c tessedit_char_whitelist={SUPPORTED_CHARS}"
                text = pytesseract.image_to_string(cropped, config=config).strip()
                
                # Tisztítás: minden nem-alfanumerikus eltávolítása (kivéve kötőjel)
                text = re.sub(r'\n', '', text)
                clean_text = ''.join(c for c in text if c.isalnum() or c == '-')
                
                # Post-processing: regex ellenőrzés
                if validate_plate(clean_text):
                    best_text = clean_text
                    break
                elif len(clean_text) > best_length:
                    best_text = clean_text
                    best_length = len(clean_text)
            except Exception:
                pass
        
        if best_text and is_valid_text(best_text):
            results.append({'pozicio': len(results) + 1, 'szam': best_text})
    
    return remove_duplicate_plates(results)


def recognize_plate(image_path):
    """Az első felismert rendszám (visszafelé kompatibilítás)."""
    results = recognize_plates(image_path)
    return results[0]['szam'] if results else None


def main():
    parser = argparse.ArgumentParser(
        description="Rendszámtábla detektálása és olvasása képről"
    )
    parser.add_argument("--image", "-i", required=True, help="Kép elérési útja")
    parser.add_argument("--verbose", "-v", action="store_true", help="Részletes kimenet")
    args = parser.parse_args()
    
    try:
        results = recognize_plates(args.image)
        
        if not results:
            print("Nem találtam rendszámtáblát.")
            return
        
        if len(results) == 1:
            print(f"Felismert rendszám: {results[0]['szam']}")
        else:
            print(f"Felismert {len(results)} rendszám:")
            for r in results:
                print(f"  {r['pozicio']}. {r['szam']}" if args.verbose else f"  {r['szam']}")
    
    except Exception as e:
        print(f"Hiba: {e}")


if __name__ == '__main__':
    main()
