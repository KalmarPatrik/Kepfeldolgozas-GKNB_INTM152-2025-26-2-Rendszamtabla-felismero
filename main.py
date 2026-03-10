#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rendszámtábla felismerő rendszer.

A pipeline három fő részből áll:
1. Többcsatornás jelöltgenerálás klasszikus képfeldolgozással
2. Perspektívakorrekció és több OCR-változat kipróbálása
3. Jogszabályalapú formátum- és mintapontozás
"""

from __future__ import annotations

import argparse
import os
import re
from dataclasses import dataclass
from typing import Callable, Optional

try:
    import cv2
    import numpy as np
    import pytesseract
    from pytesseract import Output
    from pytesseract import pytesseract as pyt_module
except ImportError as error:
    raise ImportError(
        f"Hiányzó dependency: {error}. Futtassa: pip install -r requirements.txt"
    ) from error

DEFAULT_TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(DEFAULT_TESSERACT_PATH):
    pyt_module.tesseract_cmd = DEFAULT_TESSERACT_PATH

SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-"
OCR_TIMEOUT_SECONDS = 5
OCR_PSMS = (7, 8, 13)
MAX_CANDIDATES = 6

LETTER_TO_DIGIT = {
    "O": "0",
    "Q": "0",
    "D": "0",
    "I": "1",
    "L": "1",
    "Z": "2",
    "S": "5",
    "G": "6",
    "B": "8",
    "T": "7",
}

DIGIT_TO_LETTER = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "4": "A",
    "5": "S",
    "6": "G",
    "7": "T",
    "8": "B",
}


@dataclass(frozen=True)
class PatternDefinition:
    name: str
    tokens: tuple[str, ...]
    base_score: float
    formatter: Callable[[str], str]
    strict: bool = True

    @property
    def length(self) -> int:
        return len(self.tokens)


@dataclass
class PlateRegion:
    contour: np.ndarray
    box: np.ndarray
    bbox: tuple[int, int, int, int]
    source: str
    roi_score: float


@dataclass
class OCRMatch:
    text: str
    score: float
    confidence: float
    raw_text: str
    strict: bool


STRICT_PATTERNS = (
    PatternDefinition(
        name="new_general",
        tokens=("L", "L", "L", "L", "N", "N", "N"),
        base_score=150.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="old_general",
        tokens=("L", "L", "L", "N", "N", "N"),
        base_score=145.0,
        formatter=lambda text: f"{text[:3]}-{text[3:]}",
    ),
    PatternDefinition(
        name="new_ot",
        tokens=("O", "T", "L", "L", "N", "N", "N"),
        base_score=151.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_tx",
        tokens=("T", "X", "L", "L", "N", "N", "N"),
        base_score=151.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_ba",
        tokens=("B", "A", "L", "L", "N", "N", "N"),
        base_score=151.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_ha",
        tokens=("H", "A", "L", "L", "N", "N", "N"),
        base_score=151.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_ma",
        tokens=("M", "A", "L", "L", "N", "N", "N"),
        base_score=151.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_na",
        tokens=("N", "A", "L", "L", "N", "N", "N"),
        base_score=151.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_ra",
        tokens=("R", "A", "L", "L", "N", "N", "N"),
        base_score=151.0,
        formatter=lambda text: f"{text[:2]}-{text[2:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_temp_i_black",
        tokens=("I", "N", "N", "L", "L", "N", "N"),
        base_score=142.0,
        formatter=lambda text: text,
    ),
    PatternDefinition(
        name="new_temp_i_red",
        tokens=("I", "N", "N", "N", "L", "L"),
        base_score=143.0,
        formatter=lambda text: f"{text[:4]}-{text[4:]}",
    ),
    PatternDefinition(
        name="new_temp_cd",
        tokens=("C", "D", "N", "N", "N", "N", "N", "N"),
        base_score=144.0,
        formatter=lambda text: f"{text[:2]}-{text[2:6]}-{text[6:]}",
    ),
    PatternDefinition(
        name="old_special_cd",
        tokens=("C", "D", "N", "N", "N", "N", "N", "N"),
        base_score=140.0,
        formatter=lambda text: f"{text[:2]}-{text[2:6]}-{text[6:]}",
    ),
    PatternDefinition(
        name="old_temp_sp",
        tokens=("S", "P", "N", "N", "N", "N"),
        base_score=138.0,
        formatter=lambda text: f"{text[:2]}-{text[2:]}",
    ),
    PatternDefinition(
        name="old_temp_m",
        tokens=("M", "N", "N", "N", "N", "N", "N"),
        base_score=136.0,
        formatter=lambda text: text,
    ),
    PatternDefinition(
        name="old_temp_zpev",
        tokens=("L", "N", "N", "N", "N", "N"),
        base_score=120.0,
        formatter=lambda text: text,
    ),
)

EXTENDED_PATTERNS = (
    PatternDefinition(
        name="legacy_two_letters_four_digits",
        tokens=("L", "L", "N", "N", "N", "N"),
        base_score=112.0,
        formatter=lambda text: f"{text[:2]}-{text[2:]}",
        strict=False,
    ),
    PatternDefinition(
        name="legacy_custom_seven_letters",
        tokens=("L", "L", "L", "L", "L", "L", "L"),
        base_score=82.0,
        formatter=lambda text: f"{text[:2]}-{text[2:]}",
        strict=False,
    ),
)


def read_image(image_path: str) -> np.ndarray:
    if not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)

    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    image = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"Nem olvasható kép: {image_path}")
    return image


def safe_find_contours(image: np.ndarray, mode: int, method: int) -> list[np.ndarray]:
    contours_result = cv2.findContours(image, mode, method)
    if len(contours_result) == 2:
        contours, _ = contours_result
    else:
        _, contours, _ = contours_result
    return contours


def adaptive_canny(gray: np.ndarray) -> np.ndarray:
    median = float(np.median(gray))
    lower = int(max(0, 0.66 * median))
    upper = int(min(255, 1.33 * median + 20))
    edged = cv2.Canny(gray, lower, upper)
    return cv2.morphologyEx(edged, cv2.MORPH_CLOSE, np.ones((3, 3), np.uint8))


def preprocess_image(image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.fastNlMeansDenoising(gray, None, 11, 7, 21)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    gray = clahe.apply(gray)
    gray = cv2.bilateralFilter(gray, 9, 35, 35)
    edged = adaptive_canny(gray)
    return edged, gray


def order_points(points: np.ndarray) -> np.ndarray:
    rect = np.zeros((4, 2), dtype="float32")
    sums = points.sum(axis=1)
    rect[0] = points[np.argmin(sums)]
    rect[2] = points[np.argmax(sums)]

    diffs = np.diff(points, axis=1)
    rect[1] = points[np.argmin(diffs)]
    rect[3] = points[np.argmax(diffs)]
    return rect


def expand_box(box: np.ndarray, scale_x: float = 1.08, scale_y: float = 1.15) -> np.ndarray:
    center = box.mean(axis=0)
    vectors = box - center
    vectors[:, 0] *= scale_x
    vectors[:, 1] *= scale_y
    return center + vectors


def four_point_warp(gray: np.ndarray, box: np.ndarray) -> np.ndarray:
    rect = order_points(box.astype("float32"))
    top_left, top_right, bottom_right, bottom_left = rect

    width_top = np.linalg.norm(top_right - top_left)
    width_bottom = np.linalg.norm(bottom_right - bottom_left)
    height_left = np.linalg.norm(bottom_left - top_left)
    height_right = np.linalg.norm(bottom_right - top_right)

    max_width = max(1, int(max(width_top, width_bottom)))
    max_height = max(1, int(max(height_left, height_right)))

    destination = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_height - 1],
            [0, max_height - 1],
        ],
        dtype="float32",
    )

    transform = cv2.getPerspectiveTransform(rect, destination)
    warped = cv2.warpPerspective(gray, transform, (max_width, max_height))
    if warped.shape[0] > warped.shape[1]:
        warped = cv2.rotate(warped, cv2.ROTATE_90_CLOCKWISE)
    return warped


def contour_metrics(
    contour: np.ndarray, image_width: int, image_height: int
) -> tuple[float, float, float, float]:
    (_, _), (width, height), _ = cv2.minAreaRect(contour)
    if width <= 0 or height <= 0:
        return 0.0, 0.0, 0.0, 0.0

    long_side, short_side = sorted((float(width), float(height)), reverse=True)
    area = max(long_side * short_side, 1.0)
    aspect_ratio = long_side / max(short_side, 1.0)
    area_ratio = area / max(float(image_width * image_height), 1.0)
    contour_area = cv2.contourArea(contour)
    rectangularity = contour_area / area
    return long_side, aspect_ratio, area_ratio, rectangularity


def is_valid_plate(cnt: np.ndarray, image_width: int, image_height: int) -> bool:
    long_side, aspect_ratio, area_ratio, rectangularity = contour_metrics(
        cnt, image_width, image_height
    )

    if long_side < 45:
        return False
    if not 1.6 <= aspect_ratio <= 8.5:
        return False
    if not 0.001 <= area_ratio <= 0.9:
        return False
    if rectangularity < 0.28:
        return False
    return True


def build_blackhat_mask(gray: np.ndarray) -> np.ndarray:
    kernel_width = max(15, gray.shape[1] // 18)
    kernel_height = max(3, gray.shape[0] // 80)
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (kernel_width, kernel_height))
    square_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, rect_kernel)
    gradient_x = cv2.Sobel(blackhat, cv2.CV_32F, 1, 0, ksize=-1)
    gradient_x = np.absolute(gradient_x)

    max_value = float(np.max(gradient_x))
    min_value = float(np.min(gradient_x))
    if max_value - min_value <= 1e-6:
        return np.zeros_like(gray)

    gradient_x = ((gradient_x - min_value) / (max_value - min_value) * 255).astype("uint8")
    gradient_x = cv2.morphologyEx(gradient_x, cv2.MORPH_CLOSE, rect_kernel)
    _, thresholded = cv2.threshold(gradient_x, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    thresholded = cv2.morphologyEx(thresholded, cv2.MORPH_CLOSE, square_kernel)
    thresholded = cv2.erode(thresholded, None, iterations=1)
    thresholded = cv2.dilate(thresholded, None, iterations=2)
    return thresholded


def build_adaptive_mask(gray: np.ndarray) -> np.ndarray:
    thresholded = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        7,
    )
    thresholded = cv2.bitwise_not(thresholded)
    thresholded = cv2.morphologyEx(
        thresholded,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 3)),
    )
    return cv2.dilate(thresholded, None, iterations=1)


def region_score(
    contour: np.ndarray,
    image_width: int,
    image_height: int,
    source: str,
) -> float:
    _, aspect_ratio, area_ratio, rectangularity = contour_metrics(contour, image_width, image_height)
    aspect_score = max(0.0, 32.0 - abs(aspect_ratio - 4.2) * 7.0)
    area_score = max(0.0, 22.0 - abs(area_ratio - 0.03) * 260.0)
    source_bonus = {"blackhat": 16.0, "adaptive": 10.0, "edge": 6.0}.get(source, 0.0)
    return aspect_score + area_score + rectangularity * 55.0 + source_bonus


def bbox_iou(first: tuple[int, int, int, int], second: tuple[int, int, int, int]) -> float:
    first_x, first_y, first_width, first_height = first
    second_x, second_y, second_width, second_height = second

    x_left = max(first_x, second_x)
    y_top = max(first_y, second_y)
    x_right = min(first_x + first_width, second_x + second_width)
    y_bottom = min(first_y + first_height, second_y + second_height)

    if x_right <= x_left or y_bottom <= y_top:
        return 0.0

    intersection = float((x_right - x_left) * (y_bottom - y_top))
    first_area = float(first_width * first_height)
    second_area = float(second_width * second_height)
    union = max(first_area + second_area - intersection, 1.0)
    return intersection / union


def find_all_plates(edged: np.ndarray, image_width: int, image_height: int) -> list[np.ndarray]:
    contours = safe_find_contours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    valid_contours = [cnt for cnt in contours if is_valid_plate(cnt, image_width, image_height)]
    valid_contours.sort(key=lambda contour: cv2.boundingRect(contour)[0])
    return valid_contours[:MAX_CANDIDATES]


def find_plate_regions(gray: np.ndarray, edged: np.ndarray) -> list[PlateRegion]:
    image_height, image_width = gray.shape[:2]
    contour_groups = (
        ("edge", safe_find_contours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)),
        (
            "blackhat",
            safe_find_contours(build_blackhat_mask(gray), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE),
        ),
        (
            "adaptive",
            safe_find_contours(build_adaptive_mask(gray), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE),
        ),
    )

    candidates: list[PlateRegion] = []
    for source, contours in contour_groups:
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:40]
        for contour in contours:
            if not is_valid_plate(contour, image_width, image_height):
                continue

            rectangle = cv2.minAreaRect(contour)
            box = cv2.boxPoints(rectangle)
            x, y, width, height = cv2.boundingRect(box.astype(np.int32))
            roi_score = region_score(contour, image_width, image_height, source)
            candidates.append(
                PlateRegion(
                    contour=contour,
                    box=box,
                    bbox=(x, y, width, height),
                    source=source,
                    roi_score=roi_score,
                )
            )

    candidates.sort(key=lambda region: region.roi_score, reverse=True)
    deduplicated: list[PlateRegion] = []
    for candidate in candidates:
        if any(bbox_iou(candidate.bbox, existing.bbox) > 0.55 for existing in deduplicated):
            continue
        deduplicated.append(candidate)
        if len(deduplicated) >= MAX_CANDIDATES:
            break

    if not deduplicated:
        full_box = np.array(
            [[0, 0], [image_width - 1, 0], [image_width - 1, image_height - 1], [0, image_height - 1]],
            dtype=np.float32,
        )
        deduplicated.append(
            PlateRegion(
                contour=np.array([]),
                box=full_box,
                bbox=(0, 0, image_width, image_height),
                source="fallback",
                roi_score=8.0,
            )
        )

    return deduplicated


def resize_to_target_height(image: np.ndarray, target_height: int = 110) -> np.ndarray:
    if image.size == 0:
        return image

    height, width = image.shape[:2]
    if height <= 0 or width <= 0:
        return image

    scale = target_height / float(height)
    target_width = max(1, int(width * scale))
    return cv2.resize(image, (target_width, target_height), interpolation=cv2.INTER_CUBIC)


def generate_ocr_variants(crop: np.ndarray) -> list[np.ndarray]:
    if crop.size == 0:
        return []

    normalized = resize_to_target_height(crop)
    sharpened = cv2.addWeighted(normalized, 1.4, cv2.GaussianBlur(normalized, (0, 0), 1.2), -0.4, 0)
    _, otsu = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(
        sharpened,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        31,
        5,
    )

    variants = [sharpened, otsu, adaptive]
    bordered_variants = []
    for variant in variants:
        border_value = 255 if np.mean(variant) > 127 else 0
        bordered_variants.append(
            cv2.copyMakeBorder(variant, 10, 10, 14, 14, cv2.BORDER_CONSTANT, value=border_value)
        )
    return bordered_variants


def extract_plate_crops(gray: np.ndarray, region: PlateRegion) -> list[np.ndarray]:
    expanded_box = expand_box(region.box)
    warped = four_point_warp(gray, expanded_box)

    x, y, width, height = region.bbox
    padding_x = max(4, int(width * 0.06))
    padding_y = max(4, int(height * 0.12))
    left = max(0, x - padding_x)
    top = max(0, y - padding_y)
    right = min(gray.shape[1], x + width + padding_x)
    bottom = min(gray.shape[0], y + height + padding_y)
    bounding_crop = gray[top:bottom, left:right]

    crops = []
    for crop in (warped, bounding_crop):
        if crop.size == 0:
            continue
        if crop.shape[0] > crop.shape[1]:
            crop = cv2.rotate(crop, cv2.ROTATE_90_CLOCKWISE)
        crops.append(crop)
    return crops


def read_ocr_text(image: np.ndarray, psm: int) -> tuple[str, float]:
    config = f"--psm {psm} --oem 3 -c tessedit_char_whitelist={SUPPORTED_CHARS}"
    try:
        data = pytesseract.image_to_data(
            image,
            config=config,
            output_type=Output.DICT,
            timeout=OCR_TIMEOUT_SECONDS,
        )
    except Exception:
        return "", 0.0

    tokens = []
    confidences = []
    for text, confidence in zip(data.get("text", []), data.get("conf", [])):
        if not text or not str(text).strip():
            continue
        tokens.append(str(text).strip())
        try:
            confidence_value = float(confidence)
        except (TypeError, ValueError):
            confidence_value = -1.0
        if confidence_value >= 0:
            confidences.append(confidence_value)

    raw_text = "".join(tokens).upper()
    average_confidence = float(sum(confidences) / len(confidences)) if confidences else 0.0
    return raw_text, average_confidence


def convert_char(char: str, token: str) -> Optional[tuple[str, int]]:
    if token == "L":
        if char.isalpha():
            return char, 0
        mapped = DIGIT_TO_LETTER.get(char)
        if mapped:
            return mapped, 1
        return None

    if token == "N":
        if char.isdigit():
            return char, 0
        mapped = LETTER_TO_DIGIT.get(char)
        if mapped:
            return mapped, 1
        return None

    if char == token:
        return token, 0

    if token.isalpha():
        mapped = DIGIT_TO_LETTER.get(char)
        if mapped == token:
            return token, 1
        return None

    mapped = LETTER_TO_DIGIT.get(char)
    if mapped == token:
        return token, 1
    return None


def score_candidates(
    compact_text: str,
    raw_text: str,
    confidence: float,
    roi_score: float,
) -> list[OCRMatch]:
    if len(compact_text) < 5:
        return []

    matches: dict[str, OCRMatch] = {}
    pattern_sets = STRICT_PATTERNS + EXTENDED_PATTERNS

    for pattern in pattern_sets:
        if len(compact_text) < pattern.length:
            continue

        for start_index in range(0, len(compact_text) - pattern.length + 1):
            window = compact_text[start_index:start_index + pattern.length]
            corrected = []
            conversion_cost = 0

            for current_char, current_token in zip(window, pattern.tokens):
                converted = convert_char(current_char, current_token)
                if converted is None:
                    break
                corrected_char, char_cost = converted
                corrected.append(corrected_char)
                conversion_cost += char_cost
            else:
                corrected_text = "".join(corrected)
                canonical_text = pattern.formatter(corrected_text)
                trim_penalty = start_index + (len(compact_text) - start_index - pattern.length)
                separator_bonus = 3.0 if "-" in raw_text and "-" in canonical_text else 0.0
                exact_window_bonus = 4.0 if trim_penalty == 0 else 0.0
                total_score = (
                    pattern.base_score
                    - conversion_cost * 8.5
                    - trim_penalty * 6.0
                    + separator_bonus
                    + exact_window_bonus
                    + confidence * 0.35
                    + roi_score
                )

                candidate = OCRMatch(
                    text=canonical_text,
                    score=total_score,
                    confidence=confidence,
                    raw_text=raw_text,
                    strict=pattern.strict,
                )
                existing = matches.get(candidate.text)
                if existing is None or candidate.score > existing.score:
                    matches[candidate.text] = candidate

    sorted_matches = sorted(matches.values(), key=lambda match: match.score, reverse=True)
    return sorted_matches


def normalize_plate_text(text: str) -> Optional[str]:
    raw_text = text.strip().upper()
    compact_text = re.sub(r"[^A-Z0-9]", "", raw_text)
    matches = score_candidates(compact_text, raw_text, confidence=35.0, roi_score=0.0)
    if not matches:
        return None
    best_match = matches[0]
    if best_match.strict or best_match.score >= 110.0:
        return best_match.text
    return None


def is_valid_text(text: str) -> bool:
    return normalize_plate_text(text) is not None


def validate_plate(text: str) -> bool:
    return normalize_plate_text(text) is not None


def remove_duplicate_plates(results: list[dict]) -> list[dict]:
    if len(results) <= 1:
        for index, item in enumerate(results, 1):
            item["pozicio"] = index
            item.pop("bbox", None)
            item.pop("score", None)
            item.pop("confidence", None)
        return results

    results.sort(key=lambda item: item.get("score", 0.0), reverse=True)
    filtered: list[dict] = []

    for result in results:
        duplicate_index = None
        for index, existing in enumerate(filtered):
            same_text = result["szam"] == existing["szam"]
            overlapping = bbox_iou(result["bbox"], existing["bbox"]) > 0.5
            if same_text or overlapping:
                duplicate_index = index
                break

        if duplicate_index is None:
            filtered.append(result)
            continue

        if result.get("score", 0.0) > filtered[duplicate_index].get("score", 0.0):
            filtered[duplicate_index] = result

    filtered.sort(key=lambda item: item["bbox"][0])
    for index, item in enumerate(filtered, 1):
        item["pozicio"] = index
        item.pop("bbox", None)
        item.pop("score", None)
        item.pop("confidence", None)
    return filtered


def recognize_crop(crop: np.ndarray, roi_score: float) -> Optional[OCRMatch]:
    best_match: Optional[OCRMatch] = None
    seen_raw_texts: set[tuple[str, int]] = set()

    for variant in generate_ocr_variants(crop):
        for psm in OCR_PSMS:
            raw_text, confidence = read_ocr_text(variant, psm)
            if not raw_text:
                continue

            dedupe_key = (raw_text, psm)
            if dedupe_key in seen_raw_texts:
                continue
            seen_raw_texts.add(dedupe_key)

            compact_text = re.sub(r"[^A-Z0-9]", "", raw_text)
            matches = score_candidates(compact_text, raw_text, confidence, roi_score)
            if not matches:
                continue

            current_match = matches[0]
            if best_match is None or current_match.score > best_match.score:
                best_match = current_match
                if best_match.strict and best_match.score >= 185.0:
                    return best_match

    return best_match


def recognize_plates(image_path: str) -> list[dict]:
    image = read_image(image_path)
    edged, gray = preprocess_image(image)
    regions = find_plate_regions(gray, edged)

    results = []
    for region in regions:
        region_best: Optional[OCRMatch] = None
        for crop in extract_plate_crops(gray, region):
            crop_match = recognize_crop(crop, region.roi_score)
            if crop_match is None:
                continue
            if region_best is None or crop_match.score > region_best.score:
                region_best = crop_match

        if region_best is None:
            continue
        if not region_best.strict and region_best.score < 118.0:
            continue

        results.append(
            {
                "pozicio": 0,
                "szam": region_best.text,
                "bbox": region.bbox,
                "score": region_best.score,
                "confidence": region_best.confidence,
            }
        )

    return remove_duplicate_plates(results)


def recognize_plate(image_path: str) -> Optional[str]:
    results = recognize_plates(image_path)
    return results[0]["szam"] if results else None


def main() -> None:
    parser = argparse.ArgumentParser(description="Rendszámtábla detektálása és olvasása képről")
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
            return

        print(f"Felismert {len(results)} rendszám:")
        for result in results:
            if args.verbose:
                print(f"  {result['pozicio']}. {result['szam']}")
            else:
                print(f"  {result['szam']}")
    except Exception as error:
        print(f"Hiba: {error}")


if __name__ == "__main__":
    main()