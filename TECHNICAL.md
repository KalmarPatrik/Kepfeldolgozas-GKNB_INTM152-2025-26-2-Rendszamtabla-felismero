# Technikai Dokumentáció

## Áttekintés

A rendszer klasszikus képfeldolgozási és OCR pipeline-t használ, amelyet formátum-alapú pontozás egészít ki.
A fő belépési pont a `main.py`.

## Pipeline lépések

1. `read_image(image_path)`
- Unicode-biztos képbeolvasás (`cv2.imdecode`) Windows alatt.

2. `preprocess_image(image)`
- Szürkeárnyalat
- `fastNlMeansDenoising`
- CLAHE
- Bilateral filter
- Adaptív Canny (`adaptive_canny`)

3. `find_plate_regions(gray, edged)`
- Több csatornás jelöltkeresés:
  - edge alapú kontúrok
  - blackhat maszk
  - adaptive threshold maszk
- `is_valid_plate` + `region_score`
- IoU alapú deduplikáció
- max. `MAX_CANDIDATES` régió

4. `extract_plate_crops(gray, region)`
- Min area rectangle -> pontsorrend -> perspektívakorrekció
- Kiegészített bounding-box kivágás

5. `recognize_crop(crop, roi_score)`
- Több OCR-variáns (`generate_ocr_variants`)
- Több PSM (`OCR_PSMS = (7, 8, 13)`)
- `pytesseract.image_to_data` konfidenciával

6. `score_candidates(compact_text, raw_text, confidence, roi_score)`
- Szigorú és kiterjesztett minták (`STRICT_PATTERNS`, `EXTENDED_PATTERNS`)
- Karakterkorrekció (`DIGIT_TO_LETTER`, `LETTER_TO_DIGIT`)
- Szabálypontozás, trimming büntetés, szeparátor bónusz

7. `remove_duplicate_plates(results)`
- Szöveg- és átfedés alapú deduplikáció
- Végső rendezés balról jobbra

## Publikus függvények

- `recognize_plate(image_path) -> Optional[str]`
- `recognize_plates(image_path) -> list[dict]`

`recognize_plates` visszatérési elemei:
- `pozicio`: balról-jobbra index
- `szam`: normalizált rendszám

## CLI

`main.py`

```powershell
python main.py -i "Képek\images.jpg" [-v]
```

`batch_scan.py`

```powershell
python batch_scan.py [-d "Képek"]
```

`benchmark.py`

```powershell
python benchmark.py [-d "Képek"]
```

## Konfigurációs konstansok (`main.py`)

- `SUPPORTED_CHARS`
- `OCR_TIMEOUT_SECONDS`
- `OCR_PSMS`
- `MAX_CANDIDATES`
- `DEFAULT_TESSERACT_PATH`

## Tesseract kezelés

- Ha létezik: `C:\Program Files\Tesseract-OCR\tesseract.exe`, automatikusan használja.
- Egyéb esetben a rendszer `PATH` alapján keresi.

## Ismert technikai korlátok

- OCR timeout miatt egyes nehéz képek lassabban futnak.
- A benchmark teljes képkészleten időigényes.
- A szabályalapú mintaillesztés miatt extrém formátumoknál hamis negatív előfordulhat.

## Debug eszközök

- `debug_plates.py`: OCR variánsok és PSM viselkedés
- `debug_crops.py`: valid kontúrok kivágása
- `debug_visuals.py`: edge és kontúr vizualizáció
