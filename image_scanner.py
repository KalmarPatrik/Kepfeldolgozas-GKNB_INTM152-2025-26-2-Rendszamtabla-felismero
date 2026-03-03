"""Egyszerű képfelderítő eszköz.

A szkript bejár egy megadott könyvtárat (alapértelmezetten az aktuális
könyvtárat), és azonosítja a képfájlokat, majd kiírja azok alapvető metaadatait,
például a fájl nevét, formátumát, méretét és színmódját.

Függőségek:
    Pillow

Használat:
    python image_scanner.py [--path PATH]

"""
import argparse
import os
from PIL import Image

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff"}


def scan_images(directory: str):
    """Scan the given directory recursively for images and display metadata."""

    for root, _, files in os.walk(directory):
        for file in files:
            _, ext = os.path.splitext(file)
            if ext.lower() in SUPPORTED_EXTENSIONS:
                path = os.path.join(root, file)
                try:
                    with Image.open(path) as img:
                        print(f"Talált kép: {path}")
                        print(f"  Formátum: {img.format}")
                        print(f"  Méret: {img.size}")
                        print(f"  Mód: {img.mode}\n")
                except Exception as e:
                    print(f"Hiba a(z) {path} megnyitásakor: {e}")


def main():
    parser = argparse.ArgumentParser(description="Könyvtár beolvasása képfájlok kereséséhez.")
    parser.add_argument(
        "--path", "-p", default=".", help="Beolvasandó könyvtár (alapértelmezett: aktuális könyvtár)"
    )
    args = parser.parse_args()
    scan_images(args.path)


if __name__ == "__main__":
    main()
