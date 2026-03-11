# Telepítési Útmutató

Ez a dokumentum a projekt stabil beállítását és futtatását írja le Windows környezetben.

## 1. Előfeltételek

- Python 3.8+
- Windows 10/11
- Tesseract OCR (külön telepítés)

## 2. Virtuális környezet

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Ha hiba: `running scripts is disabled on this system`

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Alternatíva aktiválás nélkül:

```powershell
.\.venv\Scripts\python.exe main.py -i "Képek\images.jpg"
```

## 3. Függőségek telepítése

```powershell
pip install -r requirements.txt
```

`requirements.txt` tartalma:
- opencv-python
- numpy
- Pillow
- scikit-image
- pytesseract

## 4. Tesseract telepítés

1. Letöltés: https://github.com/UB-Mannheim/tesseract/wiki
2. Ajánlott telepítési útvonal: `C:\Program Files\Tesseract-OCR\`
3. Ellenőrzés:

```powershell
where tesseract
& 'C:\Program Files\Tesseract-OCR\tesseract.exe' --version
```

A projektben a `main.py` automatikusan ezt a gyári útvonalat használja, ha létezik.

## 5. Futtatás

### Egy kép

```powershell
python main.py -i "Képek\images.jpg"
python main.py -i "Képek\images.jpg" -v
```

### Mappa

```powershell
python batch_scan.py
python batch_scan.py -d "Képek"
```

### Benchmark

```powershell
python benchmark.py
python benchmark.py -d "Képek"
```

## 6. Gyakori hibák

### `Activate.ps1 cannot be loaded...`

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### `No module named 'cv2'`

```powershell
pip install -r requirements.txt
```

### `tesseract is not installed or it's not in your PATH`

- Telepítsd a Tesseractot.
- Ellenőrizd: `where tesseract`
- Győződj meg róla, hogy a telepítés `C:\Program Files\Tesseract-OCR\` alatt van, vagy a saját útvonalad szerepel a `PATH` változóban.

### `Nem olvasható kép`

- Ellenőrizd az útvonalat és a fájl meglétét.
- Adj meg abszolút útvonalat.

## 7. Projekt lezárása

```powershell
deactivate
```

Ha nem aktiváltad a venv-et, nincs külön teendő.
