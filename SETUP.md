# Telepítési Útmutató – Rendszámtábla Felismerő

Ez a dokumentum részletesen ismerteti a projekt beállítását és futtatását.

---

## 1. Rendszer Követelmények

- **Python:** 3.8+
- **Operációs rendszer:** Windows 10/11
- **Disk terület:** ~500 MB (Tesseract + függőségek miatt)

---

## 2. Python Függőségek Telepítése

### 2.1 Virtual Environment Létrehozása (ajánlott)

```powershell
# A projekt könyvtárában:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2.2 Python Csomagok Telepítése

```powershell
pip install -r requirements.txt
```

A csomagok:
- **opencv-python** – Képfeldolgozás
- **numpy** – Numerikus adatkezelés
- **Pillow** – Kép manipuláció
- **scikit-image** – Továbbfejlesztett képfeldolgozás
- **pytesseract** – OCR (Optical Character Recognition) Python interfész

---

## 3. Tesseract OCR Motor Telepítése

### **Ez az legalapvetőbb lépés! A program nem működik nélküle!**

#### 3.1 Windows (Ajánlott módszer)

1. Töltsd le az **UB Mannheim** Tesseract telepítőjét:
   - Link: https://github.com/UB-Mannheim/tesseract/wiki
   - Keress rá: `tesseract-ocr-w64-setup-v5.x.exe` vagy `tesseract-ocr-w32-setup-v5.x.exe`

2. Futtasd a `.exe` fájlt és kövesd az utasításokat:
   - **Telepítési hely:** Hagyd az alapértelmezetten (`C:\Program Files\Tesseract-OCR\`)
   - **Komponensek:** Válaszd ki az **angol** (English) nyelvmodellt minimum

3. **Telepítés ellenőrzése:**

```powershell
where tesseract
# Vagy közvetlenül:
& 'C:\Program Files\Tesseract-OCR\tesseract.exe' --version
```

Ha működik, látni fogod a verzióinformációkat.

### 3.2 Egyéb Telepítési Helyek

Ha máshova telepítetted a Tesseract-et, szerkeszd meg a `main.py` fájlban a `tesseract_paths` listát:

```python
tesseract_paths = [
    r'C:\Program Files\Tesseract-OCR\tesseract.exe',  # 64-bit
    r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',  # 32-bit
    r'C:\path\to\your\tesseract.exe',  # Saját hely
]
```

---

## 4. Projekt Futtatása

### 4.1 Egyetlen Kép Feldolgozása

```powershell
# Virtual Environment aktiválása (ha használod):
.\.venv\Scripts\Activate.ps1

# Futtatás:
python main.py --image "C:\path\to\image.jpg"
```

**Kimenet:**
- Ha sikeres: `Felismert rendszám: ABC123` (vagy hasonló)
- Ha nem talál táblát: `Nem találtam rendszámtáblát a képen.`

### 4.2 Képek Mappájának Tömeges Feldolgozása

```powershell
python batch_scan.py
```

Vagy másik mappa megadásával:

```powershell
python batch_scan.py --dir "C:\path\to\images"
```

**Kimenet:** Egyenként sorolja fel az összes képfájlt a könyvtárban.

---

## 5. Hibaelhárítás

### **Hiba: "tesseract is not installed or it's not in your PATH"**

**Megoldás:**
1. Ellenőrizd, hogy a Tesseract telepítve van: `where tesseract`
2. Ha nem talált: telepítsd az UB Mannheim linkről
3. Ha telepítve van, de nem működik: frissítsd a `tesseract_paths` listát a `main.py`-ban

### **Hiba: "ModuleNotFoundError: No module named 'cv2'"**

**Megoldás:**
```powershell
pip install opencv-python
```

### **Hiba: "Az OpenCV (cv2) nincs telepítve..."**

**Megoldás:**
```powershell
pip install -r requirements.txt
```

### **Hiba: "Nem található vagy nem olvasható a kép"**

**Megoldás:**
- Ellenőrizd, hogy a fájlnév helyesen van megadva
- Győződj meg, hogy a fájl létezik
- Használj teljes (abszolút) elérési utat: `C:\Users\...\image.png`

### **Tesseract lassan működik**

- Ez normális! Az OCR feldolgozás erőforrásigényes
- Az első futtatás lassabb lehet (indexelés miatt)
- Türelmesen várd meg az eredményt

---

## 6. Konfigurálás (Haladó)

### Supported Characters

A `main.py` alapértelmezetten csak angol nagybetűket és számokat ismeri fel:

```python
SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
```

Ha módosítani akarod (pl. magyar karaktereket vagy kisbetűket is):

```python
SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
```

### OCR Beállítások

A `main.py`-ban az `recognize_plate()` függvényben módosítható az OCR konfiguráció:

```python
config = f"--psm 8 --oem 3 -c tessedit_char_whitelist={SUPPORTED_CHARS}"
```

- **--psm 8:** "Treat the image as a single word" (ajánlott rendszámokhoz)
- **--oem 3:** OCR Engine Mode (3 = legacy + LSTM)
- **tessedit_char_whitelist:** Megengedett karakterek

---

## 7. Virtual Environment Deaktiválása

```powershell
deactivate
```

---

## 8. Támogatott Képformátumok

- `.jpg`, `.jpeg`
- `.png`
- `.bmp`
- `.gif`
- `.tiff`

---

## 9. Teljesítmény Tippek

1. **Kép mérete:** Kisebb képek gyorsabban feldolgozódnak
2. **Felbontás:** Legalább 100x30 pixel szükséges a táblához
3. **Kontrasztos kép:** Jobb nyilatkozás az OCR-rel
4. **Világos háttér:** Fekete szöveg fehér háttéren ideális

---

## 10. Van-e még kérdés?

- Nézd meg a `README.md` fájlt általános információkért
- Ellenőrizd a `requirements.txt` fájlt a függőségekhez
- Tekintsd meg a `main.py` és `batch_scan.py` fájlok dokumentációs stringjeit

---

**Sok szerencsét!** 🚗📸

