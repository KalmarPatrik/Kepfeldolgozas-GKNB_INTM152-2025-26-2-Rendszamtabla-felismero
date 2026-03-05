import cv2

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # CLAHE hozzáadása
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)
    gray = cv2.bilateralFilter(gray, 11, 17, 17)
    # Canny threshold emelése (kevesebb zaj)
    edged = cv2.Canny(gray, 50, 150)  # 10 helyett 50
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
    return edged, gray