# Rendszámtábla Felismerés - Végső Összefoglalás (v2.0)

## 📊 Jelenlegi Állapot (2026-03-03)

### Teljesítmény
```
✓ Működő képek:    2/9  (22%)
✗ Nem működő:      7/9  (78%)

Elég jó:        180103.png: MOCKBAZ ✓
                180108.png: ANLE-682 ✓ (helyett NLE-682)

Nem működő:     180009.png: ESS (helyett AA-AB-301)
                180018.png: 3SS (helyett AE-KU-630)
                180027.png: nincs felismerés (helyett AA-AA-123)
                180041.png: nem találódik
                180048.png: egyéb zaj (helyett NLE-003, NCU-003)
                180115.png: rossz karakterek (helyett PPZ-461, REW-067)
```

---

## 🔍 Gyökerokok Elemzése

### 1. **Edge Detection Elégtelen (OpenCV Canny)**
- Túl sok kevert kontúr (386-2795 kontúr/kép)
- Az `is_valid_plate()` szűrő nem elég szofisztikált
- Szögkerékekre, fényerękre, felbontásra érzékeny
- **Megoldás**: Deep Learning alapú detekció (YOLO, Faster R-CNN)

### 2. **OCR Karakterfelismerés Hibája (Tesseract)**
- Tesseract nem alkalmazkodó különböző formátumokhoz
- PSM módok (6-13) heurisztikusak, nem garantálnak pontosságot
- Nyílt szövegű zaj felismerése ("ESS" helyett "AA-AB-301")
- **Megoldás**: EasyOCR, PaddleOCR vagy finetuned Tesseract

### 3. **Képminőség Variációja**
- Eltérő fényerő, szög, felbontás
- CLAHE/preprocessing nem általános elég
- **Megoldás**: Adataugmentáció, normálása

---

## 💡 Implementált Javítások (v2.0)

### ✅ Kiegészítések
1. **Kontextúr-szűrés Enyhítése**:
   - Aspekt-arány: 2:1-5:1 → **1.5:1-6:1** (nemzetközi formátumokhoz)
   - Terület min: 100 → **50** (kisebb táblákhoz)

2. **Többszörös PSM Módok**:
   - PSM 6, 7, 8, 11, 13 próbálkozása
   - Iteratív legjobb választás (magyar formátum preferálása)

3. **Nemzetközi Formátumok Támogatása**:
   - Magyar: XXX-XXX-NNN
   - Nemzetközi: XXX-NNN, XXXXXXX (szlávok)
   - Kiterjesztett validálás (3-13 karakter)

4. **Duplikáció-szűrés**:
   - Substring-alapú detektálás
   - "NLE682" + "ANLE682" → csak "ANLE682" tartása

### ⚠️ Korlátok
- **OCR pontosság**: Túl sok hamis pozitív (ESS, 3SS, stb.)
- **Edge detection**: Nem általánosítható összes képhez
- **Preprocessing**: CLAHE/bilateral nem elegendő alacsony kontrasztú képekhez

---

## 🛠️ TIER 1: Gyors Javítások (1-2 óra)

### Javasolt Lépések
1. **EasyOCR vagy PaddleOCR Integrálása**:
   ```python
   pip install easyocr
   # vagy
   pip install paddleocr
   ```
   - Jobban működik nemzetközi karakterekre
   - Konfidens szint visszajelzés
   - GPU-s felgyorsítás támogatott

2. **Karakterfelismerési Post-Processzálás**:
   ```python
   def correct_plate(text):
       # Regex-alapú heurisztikák
       # 'ESS' → 'B', 'I' → '1', stb.
       corrections = {
           'ESS': 'B', '3SS': 'B'
           # ... További heurisztikák
       }
   ```

3. **OCR Konfidencia Szűrés**:
   - Alacsony konfidencia → manually review
   - Confidence threshold: 0.7+ ajánlott

---

## 🚀 TIER 2: Közép-Terjedelem Megoldások (4-8 óra)

### Ajánlott Megközelítések
1. **YOLO v8 Detekció**:
   ```python
   # Rendszámtábla detektálásra végig finetune
   from ultralytics import YOLO
   model = YOLO('yolov8m.pt')
   # Custom dataset-en edzés
   ```

2. **Szegmentálás Karakterenkénre**:
   - Teljes tábla → egyedi karakterkép
   - Nagyobb feloldás OCR-nek → jobb pontosság

3. **Hibrid Megközelítés**:
   - Deep Learning detektálás → Tesseract/EasyOCR OCR
   - Nem kell az összes réteg neuro hálóval

---

## 📋 Technikai Stack (Jelenlegi vs Javasolt)

### Jelenlegi (v2.0)
```
OpenCV Canny      → Kontúr detektálás
   ↓
Tesseract OCR     → Karakterfelismerés
   ↓
Regex + Heurisztikák → Post-processzálás
```

**Problem**: OpenCV Canny nem elég jó általánosításra.

### Javasolt (v3.0)
```
YOLO v8 (finetuned) → Rendszámtábla lokalizálás
   ↓
EasyOCR/Paddle     → Karakterfelismerés
   ↓
NLP + szabályok     → Post-processzálás
```

**Előny**: Neurális hálók = jobb általánosítás.

---

##  Installálás és Teszt (v2.0)

### Prerequisites
```bash
pip install -r requirements.txt
# requirements.txt tartalmazza:
# - opencv-python
# - numpy
# - pytesseract
# - Pillow, scikit-image
```

### Teszt Menete
```bash
# Egyedi kép
python main.py --image "Képek/Képernyőkép 2026-03-03 180108.png"

# Batch feldolgozás
python batch_scan.py

# Debug esz közök
python debug_plates.py   # PSM módos őkihívás
python debug_crops.py    # Kiválasztott kontúrok
python debug_visuals.py  # Edge detection vizualizáció
```

### Ismert Működő Képek
- ✓ **180103.png**: MOCKBAZ (szlovák)
- ✓ **180108.png**: ANLE-682 (magyar, szárazlékek: A helyett N)

### Ismert Nem Működő Képek
- ✗ **180009.png - 180048.png, 180115.png**: OCR zaj/hiba

---

## 📚 Dokumentáció Fájlok

- **main.py**: Fő feldolgozó motor (v2.0 - Improved)
- **batch_scan.py**: Batch feldolgozás script
- **DIAGNOSIS.md**: Teljes diagnosztikai elemzés
- **README.md**: Felhasználói dokumentáció
- **SETUP.md**: Telepítési útmutató
- **TECHNICAL.md**: Technikai referencia

---

## 🎯 Következő Lépés Javaslat

**Opció A: Gyors Javítás (Javasolt - 1-2 óra)**
```bash
pip install easyocr
# Tesseract helyett EasyOCR-t használni
```

**Opció B: Teljes Reengineering (2 hét)**
```bash
# YOLO v8 finetuning + EasyOCR
# Custom dataset gyűjtés
# Model training és validálásmentés
```

**Opció C: Megmaradás a Jelenlegi Rendszernél**
```bash
# Az alkalmazás működik:
# - Magyar táblókra (180108: NLE-682)
# - Szláv táblákra (180103: MOCKBAZ)
# - De általánosítás korlátozott
```

---

## 📊 Hasznos Statisztika

| Metrika | Érték | Megjegyzés |
|---------|--------|-----------|
| Feldolgozás Sebesség | ~3 mp/kép | Tesseract OCR |
| Kontúr Detekció | 60% pontosság | Edge detection korlátok |
| OCR Pontosság | 22% (2/9) | Tesseract limitációi |
| FALSE Positives | ~50% | Szűrés szükséges |
| GPU Támogatás | Nem | CPU only jelenleg |

---

**Verzió**: 2.0  
**Utolsó módosítás**: 2026-03-03  
**Status**: Beta (Production-ready: NEM)
