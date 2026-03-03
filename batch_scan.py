"""Batch feldolgozás a Képek mappában található képekre.

A program beolvassa a könyvtár összes fájlját és minden képen megpróbálja
felismerni a rendszámot a `main.recognize_plate` függvénnyel.
A kimenetet könnyen át lehet nézni a terminálban, hasonló formátumban,
melyből könnyen készülhet jelentmezonysejtett.

Használat:
    python batch_scan.py [--dir PATH]

A `--dir` paraméterrel másik mappát is megadhatsz (alapértelmezett: "Képek").

Példa:
    python batch_scan.py                 # "Képek" mappára gondol
    python batch_scan.py --dir "Képek"  # Explicit megadás
    python batch_scan.py -d "C:\\images" # Másik mappa

Kimenet példa:
    Képernyőkép 2026-03-03 180009.png: nincs tábla
    Képernyőkép 2026-03-03 180018.png: ABC1234
    Képernyőkép 2026-03-03 180027.png: hiba (nem képfájl)
"""

import argparse
import os
from main import recognize_plates


def scan_directory(directory: str):
    """A megadott könyvtár összes képét feldolgozza, több rendszámot is detektálva.
    
    Args:
        directory (str): A beolvasandó könyvtár adott elérési útja.
    """
    print(f"\n=== Feldolgozás indul: {directory} ===")
    print(f"Képek keresése...\n")
    
    found_count = 0
    error_count = 0
    plates_found = 0
    
    for root, _, files in os.walk(directory):
        for file in files:
            # Képtípusok ellenőrzése egyszerűen kiterjesztés alapján
            ext = os.path.splitext(file)[1].lower()
            if ext in {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}:
                found_count += 1
                path = os.path.join(root, file)
                try:
                    plates = recognize_plates(path)
                    if plates:
                        print(f"[OK] {file}:")
                        for plate in plates:
                            print(f"   {plate['pozicio']}. {plate['szam']}")
                        plates_found += len(plates)
                    else:
                        print(f"[-] {file}: nincs tábla")
                except Exception as e:
                    print(f"[!] {file}: hiba ({str(e)[:50]})")
                    error_count += 1
    
    # Összegzés
    print(f"\n=== Feldolgozás kész ===")
    print(f"Feldolgozva: {found_count} kép")
    print(f"Talált rendszámok: {plates_found}")
    print(f"Hibás: {error_count}")


def main():
    parser = argparse.ArgumentParser(description="Képek mappájának tömeges feldolgozása.")
    parser.add_argument(
        "--dir", "-d", default="Képek",
        help="Beolvasandó könyvtár (alapértelmezett: Képek)"
    )
    args = parser.parse_args()
    scan_directory(args.dir)


if __name__ == '__main__':
    main()
