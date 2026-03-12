# Konzultációs Dokumentum — GKNB_INTM152 Képfeldolgozás
**Dátum:** 2026-03-12

---

## 1. A feladat

Gépjárművek rendszámtáblájának automatikus detektálása és szövegfelismerése fényképekről Python segítségével.

---

## 2. Technológiai stack

| Réteg | Eszköz | Cél |
|---|---|---|
| Képfeldolgozás | OpenCV | Előfeldolgozás, kontúrdetektálás |
| OCR | Tesseract + pytesseract | Szövegfelismerés |
| Poszt-feldolgozás | Python (saját) | Formátum-alapú pontozás, normalizálás |

---

## 3. Pipeline lépései

```
Bemeneti kép
   ↓
Előfeldolgozás
  - Szürkeskála + denoise (fastNlMeansDenoising)
  - CLAHE (kontrasztjavítás)
  - Bilateral filter (élmegőrző zajszűrés)
  - Adaptív Canny (medián-alapú küszöbszámítás)
   ↓
Régiójelölt-keresés (3 csatorna párhuzamosan)
  - Canny élek → kontúrok
  - Blackhat morfológia → sötét szöveg detektálás
  - Adaptív threshold → karakterrégió
   ↓
Szűrés + deduplikáció
  - is_valid_plate(): arány, méret, négyszögletűség
  - IoU-alapú átfedésszűrés
  - Top-6 jelölt megtartása
   ↓
Kivágás + perspektívakorrekció
  - minAreaRect → 4 sarokpont rendezés
  - warpPerspective
   ↓
OCR (Tesseract)
  - 3 kép-variáns (normalize / Otsu / adaptive)
  - 3 PSM mód: 7, 8, 13
  - Konfidencia visszaolvasás (image_to_data)
   ↓
Pontozás és normalizálás
  - 18 szigorú + 2 kiterjesztett HU rendszámformátum
  - Karakter-korrekció (pl. 0↔O, 1↔I, 5↔S)
  - Formátumsor szerint kötőjel-elhelyezés
   ↓
Kimenet: rendszám(ok) balról jobbra
```

---

## 4. Fájlstruktúra

```
main.py            ← fő motor (felismerési pipeline)
batch_scan.py      ← mappa kötegelt feldolgozása
benchmark.py       ← pontossági mérés referencia-halmazra
debug_plates.py    ← OCR/PSM variánsok vizsgálata
debug_crops.py     ← detektált kivágások mentése
debug_visuals.py   ← él- és kontúrképek mentése
requirements.txt
Képek/             ← 17 tesztkép (különböző formátumok)
docs/
  HU_PLATE_FORMATS.md  ← rendszám-formátumok jogszabályi leírása
```

---

## 5. Demo parancsok

```powershell
# Aktiválás
.\.venv\Scripts\Activate.ps1
# (Ha tiltja: Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass)

# Egy kép
python main.py -i "Képek\images.jpg" -v

# Egész mappa
python batch_scan.py -d "Képek"

# Benchmark
python benchmark.py -d "Képek"
```

---

## 6. Benchmark eredmények

A rendszert 8 felcímkézett képen mértem (`EXPECTED_PLATES` a `benchmark.py`-ban):

| Metrika | Eredmény |
|---|---|
| Képszintű pontosság | 2 / 8 = **25%** |
| Rendszámszintű recall | 3 / 10 = **30%** |
| Összes feldolgozott kép | 17 |
| Találatot adó képek | 15 / 17 |

Néhány megfigyelt találat:

| Kép | Elvárt | Kapott |
|---|---|---|
| images.jpg | — | TR-AP-235 ✓ |
| 180108.png | NLE-682 | NLE-682 ✓ |
| 180027.png | AA-AA-123 | AA-AA-123 ✓ |
| 180018.png | AE-KU-630 | AE-KU-636 ≈ |
| zold_rendszamtabla.jpg | — | NLE-003 |

---

## 7. Erősségek

- Több detektálási csatorna párhuzamosan (robusztusabb jelölt-lefedettség).
- Perspektívakorrekció → döntött/szöges fotóknál is működik.
- Formátum-pontozás jogszabályi mintakészlettel (18 szigorú szabály).
- Karakterkorrekció csökkenti a Tesseract jellemző tévesztéseit.
- Unicode-biztos fájlbeolvasás Windows alatt (`cv2.imdecode`).

---

## 8. Korlátok és következő lépések

| Korlát | Rövid távú javítás | Középtávú megoldás |
|---|---|---|
| Tesseract OCR gyenge kontrasztú képeken | PSM/timeout finomhangolás | EasyOCR / PaddleOCR csere |
| Hamis pozitívok komplex háttérrel | Régió-szűrő szigorítás | ML-alapú detektor (pl. YOLO) |
| Benchmark lassú (~2-3 mp/kép) | - | GPU-s OCR motor |

---

## 9. Összefoglalás

A rendszer egy stabil, klasszikus CV + szabályalapú baseline, amely működő eredményeket ad egyértelmű képeken. A pipeline jól bővíthető: a detektálási réteg és az OCR réteg egymástól független cserélhető komponensek.
