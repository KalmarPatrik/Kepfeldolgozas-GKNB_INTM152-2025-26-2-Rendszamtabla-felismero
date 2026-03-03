# Rendszámtábla Felismerés - Diagnosztika és Javítási Terv

## 📊 Diagnózis

### Jelenlegi Teljesítmény
- **Működik jól**: 180103.png (MOCKBAZ), 180108.png (NLE-682)
- **Működik részben**: Számos kép detektálódik, de OCR helytelenül működik  
- **Nem működik**: Legtöbb kép OCR kimenetete zaj/rossz характерек

### Gyökereset Problémák

#### 1. **Edge Detection Limitációi** (OpenCV Canny)
```
Képenként detektált kontúrök:
- 180009.png: 634 kontúr → 1 valid → OCR: 'ESS' (rossz)
- 180018.png: 1430 kontúr → 4 valid → OCR: szöveg és szám,de rossz formátum
- 180048.png: 535 kontúr → 1 valid → OCR: 'P' (összefogyott)
- 180103.png: 2795 kontúr → 4 valid → OCR: 'MOCKBAZ' (jó!)
- 180108.png: 574 kontúr → 3 valid → OCR: 'NLE-682' (jó!)
```

**Probléma**: Az edge detection túl sok zaj jelölödik meg, az `is_valid_plate()` szűrő pedig nem elég finomítható, hogy kiválogassa a valódi rendszámtáblát.

#### 2. **OCR Karakterfelismerés Hibája**
```
Várt vs Kapott:
- 'AA-AB-301' ← 'ESS' (OCR nem ismeri fel a számokat/betűket)
- 'AE-KU-630' ← 'SN', 'S' (részleges felismerés + zaj)
- 'AA-AA-123' ← '-SIAASAA-123' (összekeveródött, többsoros)
- 'NLE-003' ← 'P' (karakterömlés)
- 'PPZ-461' ← 'SS', 'LH' (rossz karakterek)
```

**Probléma**: Tesseract OCR nem tisztelem az ezekhez szükséges felismerési pontosságot. PSM módok (6-13) mind rossz köputot adnak. A `SUPPORTED_CHARS` szűrő nem működik hatékonyan. Az OCR bemenetét rossz karakterek/zajuzennet terhelik.

#### 3. **Kép Komplexitása**
- **Fényerő**: Eltérő - CLAHE beépítése sem elég
- **Szög**: Néhány kép ferdeséggel fotózódott
- **Felbontás**: Eltérő karakterméretúk
- **Kontraszt**: Alacsony több képen

### Verifikáció

**Vizuális ellenőrzés (debug_crops outputok)**:
```
180108.png: 
  ✓ Kontúr #1 (236×67): Valós rendszámtábla → OCR véleménye: 'ANLE-682' (vagy 'NLE-682')
  ✓ Kontúr #2 (212×65): Valós rendszámtábla → OCR véleménye: 'NLE-682' - HELYES
```

Ez azt jelenti: a **kontúr detektálása többnyire jó**, az **OCR pedig gyakran rossz**.

---

## 🔧 Javasolt Javítások (prioritás szerint)

### TIER 1: Gyors Megoldások (napi alap működéshez)
1. **OCR Post-processzálás**: Regex-alapú karakterjavítás
   - 'ESS' → 'Y' (korrekció alapmintán)
   - '-SIAASAA-123' → 'AA-AA-123' (kötőjel-alapú szegmentálás)

2. **Karakterfelismerés Módosítása**:
   - Tesseract konfig: `--dpi 300` (ha lehetséges)
   - PSM módok szisztematikus rangsorolása (nem csak циклus)
   - Kontraszt javítás előfeldolgozásban (CLAHE aktiválása)

3. **Felismerési Bizalom Treshold**:
   - Konfidencia szint bevezetése az OCR-ből
   - Alacsony konfidencia = postprocessing/javítás szükséges

### TIER 2: Közép-terjedelem Javítások (hét)
1. **Alternatív Edge Detection Algoritmusok**:
   - Hough vonal detektálás (rendszámtáblák általában téglalap alakúak)
   - Wavelet vagy Gabor filterek
   - Deep Learning alapú detekció (YOLO v8, layoutparser)

2. **Szegmentálás Javítása**:
   - Karakterenkénti szegmentálás az aggregált képből
   - Többszintes feldolgozás (kontúr → szegmens → karakter)

3. **OCR Motor Alternatívái**:
   - EasyOCR (könnyebb, több nyelv)
   - PaddleOCR (gyorsabb, pontos)
   - MMOCR (moduláris megközelítés)

### TIER 3: Hosszú Távú Megoldások (hónapok)
1. **Deep Learning Model Edzése**:
   - Szöalap mintán YOLO detekció
   - Fine-tune Tesseract vagy alternatív OCR

2. **Többoldalú Feldolgozás**:
   - Karakterenként feldolgozni
   - Szövegfelismerés + nyelvtan validálás kombinálása

---

## 📋 Aktuális Alkarma (main.py)

### ✅ Implementált
- [x] Canny edge detection (paraméterezhető)
- [x] Négyszögletű kontúr szűrés
- [x] Aspekt-arány validáció (1.5:1 - 6:1)
- [x] Többszörös PSM módok (6, 7, 8, 11, 13)
- [x] Nemzetközi formátum támogatás
- [x] Unicode path handle (Windows)
- [x] Batch processzálás

### ⚠️ Behatárolt Működés
- [⚠️] OCR pontosság (csak egyértelű képekre működik)
- [⚠️] Edge detection általánosítása (szögekre, feltételekre érzékeny)
- [⚠️] Zajelnyomás (túl sok hamis pozitív)

### ❌ Nem Implementált
- [ ] OCR post-processzálás / karakterjavítás
- [ ] Deep Learning alapú detekció
- [ ] Karakterenkénti feldolgozás
- [ ] Több OCR motor kombinálása
- [ ] Szögkorrekció (deskew)

---

## 🎯 Javasolt Legközelebbi Lépés

**Valasztható opciók**:

### Opció A: Gyors Javítás (1-2 óra)
- OCR post-processzálás regex-alapú karakterjavításhoz
- Tesseract config finomítása (dpi, ösd módok rangsorolása)
- CLAHE betöltésé aktiválása összes képhez

### Opció B: Közepes Javítás (4-8 óra) 
- Hough vonal detektálás tesztelése
- EasyOCR vagy PaddleOCR integrálása
- Szegmentálás karakterenkénti feldolgozásra

### Opció C: Hosszú Távú Megoldás (1-2 hét)
- YOLO v8 objektum detekciós modell edzése (rendszámtáblára)
- Fine-tune OCR modell magyar/nemzetközi rendszámokra
- Teljes feldolgozási pipeline újraépítése

---

## 📝 Teszt Eredmények

### Aktuális Állapot (2026-03-03)
```
[OK] 180108.png: 1. NLE-682  ✓ Helyes
[OK] 180103.png: 1. MOCKBAZ ✓ Helyes  
[-]  180009.png: ESS (ESS helyett AA-AB-301)
[-]  180018.png: SN (helyett AE-KU-630)
[!]  180027.png: többsoros zaj
[!]  180041.png: szétszórt karakterek
[!]  180048.png: 'P' (helyett NLE-003, NCU-003)
[!]  180115.png: 'SS', 'LH' (helyett PPZ-461, REW-067)
```

**Siker arány**: 2/9 (22%)

---

## 🔗 Hivatkozások
- Tesseract PSM módok: https://tesseract-ocr.github.io/tessdoc/ImproveQuality
- EasyOCR: https://github.com/JaidedAI/EasyOCR
- PaddleOCR: https://github.com/PaddlePaddle/PaddleOCR
- YOLO v8: https://docs.ultralytics.com/
