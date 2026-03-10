#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Teljes benchmark a képmappára, címkézett és címkézetlen képekkel."""

from __future__ import annotations

import argparse
import os
from typing import Iterable

from main import recognize_plates

EXPECTED_PLATES = {
    "Képernyőkép 2026-03-03 180009.png": ["AA-AB-301"],
    "Képernyőkép 2026-03-03 180018.png": ["AE-KU-630"],
    "Képernyőkép 2026-03-03 180027.png": ["AA-AA-123"],
    "Képernyőkép 2026-03-03 180041.png": ["AA-KA-266"],
    "Képernyőkép 2026-03-03 180048.png": ["NLE-003", "NCU-003"],
    "Képernyőkép 2026-03-03 180103.png": ["MO-CKBAZ"],
    "Képernyőkép 2026-03-03 180108.png": ["NLE-682"],
    "Képernyőkép 2026-03-03 180115.png": ["PPZ-461", "REW-067"],
}

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif"}


def iter_images(directory: str) -> Iterable[str]:
    for root, _, files in os.walk(directory):
        for filename in sorted(files):
            extension = os.path.splitext(filename)[1].lower()
            if extension in IMAGE_EXTENSIONS:
                yield os.path.join(root, filename)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark a teljes képkészletre.")
    parser.add_argument("--dir", "-d", default="Képek", help="Képmappa elérési útja")
    args = parser.parse_args()

    image_count = 0
    images_with_detection = 0
    labeled_images = 0
    exact_image_matches = 0
    expected_plate_total = 0
    correct_plate_total = 0
    error_count = 0

    print(f"Benchmark indul: {args.dir}\n")

    for image_path in iter_images(args.dir):
        image_count += 1
        filename = os.path.basename(image_path)
        try:
            detections = [plate["szam"] for plate in recognize_plates(image_path)]
        except Exception as error:
            error_count += 1
            print(f"{filename}: hiba ({error})")
            continue

        if detections:
            images_with_detection += 1

        print(f"{filename}: {detections if detections else 'nincs találat'}")

        expected = EXPECTED_PLATES.get(filename)
        if expected is None:
            continue

        labeled_images += 1
        expected_plate_total += len(expected)
        exact_image_matches += int(detections == expected)
        correct_plate_total += sum(1 for plate in expected if plate in detections)

    print("\n=== Összegzés ===")
    print(f"Összes feldolgozott kép: {image_count}")
    print(f"Találatot adó képek: {images_with_detection}")
    print(f"Hibás futások: {error_count}")

    if labeled_images:
        image_accuracy = exact_image_matches / labeled_images * 100.0
        plate_accuracy = correct_plate_total / expected_plate_total * 100.0 if expected_plate_total else 0.0
        print(f"Címkézett képek száma: {labeled_images}")
        print(f"Képszintű pontosság: {exact_image_matches}/{labeled_images} = {image_accuracy:.1f}%")
        print(
            f"Rendszámszintű találati arány: {correct_plate_total}/{expected_plate_total} = {plate_accuracy:.1f}%"
        )
    else:
        print("Nem volt címkézett referencia a képek között.")


if __name__ == "__main__":
    main()