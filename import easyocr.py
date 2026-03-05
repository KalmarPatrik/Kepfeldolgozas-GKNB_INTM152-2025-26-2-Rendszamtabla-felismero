import easyocr

reader = easyocr.Reader(['en'])  # Inicializáld egyszer

# A recognize_plates függvényben, a cropped után:
cropped = cv2.resize(cropped, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)  # Nagyítás
_, cropped = cv2.threshold(cropped, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # Threshold

# Helyett pytesseract:
results = reader.readtext(cropped)
text = ''.join([res[1] for res in results if res[2] > 0.5])  # Csak magas confidence