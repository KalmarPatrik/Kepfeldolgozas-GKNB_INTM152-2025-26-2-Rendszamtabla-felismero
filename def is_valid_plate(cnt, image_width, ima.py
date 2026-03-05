def is_valid_plate(cnt, image_width, image_height):
    peri = cv2.arcLength(cnt, True)
    approx = cv2.approxPolyDP(cnt, 0.018 * peri, True)
    if len(approx) != 4:
        return False
    
    x, y, w, h = cv2.boundingRect(approx)
    aspect_ratio = float(w) / h
    if not (2.0 <= aspect_ratio <= 4.0):  # Szűkebb tartomány
        return False
    
    area = cv2.contourArea(cnt)
    min_area = (image_width * image_height) * 0.005  # 0.5% minimum
    max_area = (image_width * image_height) * 0.05   # 5% maximum
    return min_area <= area <= max_area

    hull = cv2.convexHull(cnt)
    hull_area = cv2.contourArea(hull)
    solidity = float(area) / hull_area if hull_area > 0 else 0
    if solidity < 0.7:  # Legalább 70% tömör
        return False