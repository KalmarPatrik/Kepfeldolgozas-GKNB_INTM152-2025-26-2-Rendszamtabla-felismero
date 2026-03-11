# Rendszámtábla Felismerő Rendszer

Python-alapú rendszámtábla-felismerő projekt OpenCV + Tesseract OCR alapon.
A rendszer egy képen több táblát is tud kezelni, és formátum-alapú pontozással szűri a találatokat.

## Gyors indítás

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Ha ExecutionPolicy hiba van:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python main.py -i "Képek\images.jpg"
```

Aktiválás nélkül is futtatható:

```powershell
.\.venv\Scripts\python.exe main.py -i "Képek\images.jpg"
```

## Fő parancsok

```powershell
# Egy kép feldolgozása
python main.py -i "Képek\images.jpg"

# Részletes kimenet
python main.py -i "Képek\images.jpg" -v

# Mappa feldolgozása
python batch_scan.py
python batch_scan.py -d "Képek"

# Benchmark referenciahalmazzal
python benchmark.py
```

## Példa kimenet

```text
Felismert rendszám: TR-AP-235
```

```text
[OK] image1.jpg:
   1. AA-AB-123
[-] image2.jpg: nincs tábla
[!] image3.jpg: hiba (...)
```

## Projektfájlok

```text
main.py            # Fő felismerő motor
batch_scan.py      # Kötegelt feldolgozás
benchmark.py       # Egyszerű pontossági benchmark
debug_plates.py    # OCR / PSM debug
debug_crops.py     # Detektált kivágások mentése
debug_visuals.py   # Élkép és kontúr vizualizálása
requirements.txt
QUICKREF.md
SETUP.md
TECHNICAL.md
SUMMARY.md
DIAGNOSIS.md
Képek/
```

## Működési vázlat

1. `preprocess_image`: denoise + CLAHE + bilateral + adaptív Canny.
2. `find_plate_regions`: több maszkból kontúrjelöltek gyűjtése.
3. `extract_plate_crops`: perspektívakorrekció és kivágások.
4. `read_ocr_text`: több OCR variáns és PSM mód futtatása.
5. `score_candidates`: szabályalapú mintapontozás (HU formátumokkal).
6. `remove_duplicate_plates`: átfedés/szöveg szerint duplikátumszűrés.

## Fontos megjegyzések

- Tesseract OCR telepítése kötelező.
- A projekt Windowsra van optimalizálva (Unicode fájlnevek kezelése `cv2.imdecode`-dal).
- `benchmark.py` teljes futása a képmérettől és OCR timeouttól függően hosszabb lehet.

## Dokumentáció

- `SETUP.md`: részletes telepítés és hibaelhárítás
- `QUICKREF.md`: rövid parancslista
- `TECHNICAL.md`: architektúra és algoritmus
- `SUMMARY.md`: konzultációs összefoglaló
- `DIAGNOSIS.md`: ismert kockázatok és javítási javaslatok

## Licenc

MIT - lásd: `LICENSE`.
