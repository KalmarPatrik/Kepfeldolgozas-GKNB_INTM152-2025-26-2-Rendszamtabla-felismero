# main.py

"""
Main entry point for License Plate Recognition Application

A program a megadott képfájlból megpróbálja detektálni a rendszámtáblát és
elolvasni a rajta szereplő szöveget. A felismerés OpenCV alapú előfeldolgozással
és a Tesseract OCR motor használatával történik.
"""

import argparse
import cv2
import numpy as np
import pytesseract


SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def preprocess_image(image):
    """Előkészíti a képet a rendszámtábla kereséséhez.

    1. Szürkeárnyalatosra konvertáljuk.
    2. Bilaterális szűrővel csökkentjük a zajt, miközben az élek élesek maradnak.
    3. Canny-élérzékelőt alkalmazunk.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(gray, 30, 200)
    return edged, gray


def find_plate_contour(edged):
    """Keresi a legnagyobb, négyszögletű kontúrt, ami feltételezhetően a tábla."""
    contours, _ = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:30]
    for cnt in contours:
        peri = cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, 0.018 * peri, True)
        if len(approx) == 4:
            return approx
    return None


def recognize_plate(image_path):
    """Megpróbálja felismerni a rendszámtáblát a megadott képen.

    Args:
        image_path (str): a bemeneti kép fájlneve/elérési útja.

    Returns:
        str | None: a felismert karakterlánc, vagy `None`, ha nem sikerült táblát
        találni a képen.
    """
    image = cv2.imread(image_path)
    if image is None:
        raise FileNotFoundError(f"Nem található a kép: {image_path}")

    edged, gray = preprocess_image(image)
    plate_cnt = find_plate_contour(edged)
    if plate_cnt is None:
        return None

    # Maszk készítése a kontúrhoz, majd kivágás
    mask = np.zeros(gray.shape, np.uint8)
    cv2.drawContours(mask, [plate_cnt], 0, 255, -1)
    (x, y) = np.where(mask == 255)
    (topx, topy) = (np.min(x), np.min(y))
    (bottomx, bottomy) = (np.max(x), np.max(y))
    cropped = gray[topx:bottomx+1, topy:bottomy+1]

    # OCR konfiguráció – csak engedélyezett karakterek
    config = f"--psm 8 --oem 3 -c tessedit_char_whitelist={SUPPORTED_CHARS}"
    text = pytesseract.image_to_string(cropped, config=config)
    return text.strip()


def main():
    parser = argparse.ArgumentParser(description="Rendszámtábla detektálása és olvasása képről.")
    parser.add_argument("--image", "-i", required=True, help="A beolvasandó kép elérési útja")
    args = parser.parse_args()

    try:
        result = recognize_plate(args.image)
        if result:
            print(f"Felismert rendszám: {result}")
        else:
            print("Nem találtam rendszámtáblát a képen.")
    except Exception as e:
        print(f"Hiba: {e}")


if __name__ == '__main__':
    main()
