# 🚗 Rendszámtábla Felismerő Rendszer

Egy Python-alapú alkalmazás a gépjárművek rendszámtáblájának automatikus detektálásához és szövegfelismeréséhez képek alapján.

---

## 📋 Jellemzők

- ✅ **Automatikus detektálás:** OpenCV-vel pixelszintű képfeldolgozás
- ✅ **OCR technológia:** Tesseract szövegfelismerés
- ✅ **Több rendszám felismerése:** Egy képen akár több táblát is azonosít
- ✅ **Valódiság-szűrés:** Kitevő hamis pozitívok szűrése
- ✅ **Sorszamozás:** Bal-jobb szerinti sorrend szerint számozzuk meg a talált táblákat
- ✅ **Kötegelt feldolgozás:** Több kép automatikus feldolgozása
- ✅ **Magyar interfész:** Teljes magyar nyelvű dokumentáció
- ✅ **Robusztus hibakezelés:** Részletes hibaüzenetek

---

## 🚀 Gyors Start

### 1. Telepítés

```powershell
# 1. Virtual Environment
python -m venv .venv
./.venv/Scripts/Activate.ps1

# 2. Python csomagok
pip install -r requirements.txt

# 3. Tesseract OCR (!!!FONTOS!!!)
# Letöltés: https://github.com/UB-Mannheim/tesseract/wiki
```

**Igen, a Tesseract szükséges a program működéséhez!**

### 2. Futtatás

```powershell
# Egyetlen kép:
python main.py --image "path/to/image.jpg"

# Több kép (Képek mappa):
python batch_scan.py
```

---

## 📖 Részletes Dokumentáció

A teljes telepítési útmutató és hibaelhárítás a **[SETUP.md](SETUP.md)** fájlban található.

---

## 📁 Fájlstruktúra

```
.
├── main.py                  # Fő alkalmazás (képfeldolgozás + OCR)
├── batch_scan.py            # Kötegelt feldolgozás
├── image_scanner.py         # Képek metaadatainak kiolvasása
├── requirements.txt         # Python függőségek
├── README.md                # Projekt leírása (ez a fájl)
├── SETUP.md                 # Telepítési útmutató
└── Képek/                   # Bemenet képek mappája
    ├── Képernyőkép 2026-03-03 180009.png
    ├── Képernyőkép 2026-03-03 180018.png
    └── ...
```

---

## 🛠️ Technológiai Stack

| Komponens | Leírás |
|-----------|--------|
| **Python 3.9** | Program jezik |
| **OpenCV** | Képfeldolgozás, kontúrdetektálás |
| **NumPy** | Numerikus adatkezelés |
| **Tesseract OCR** | Szövegfelismerés (optikai jelekennyegitás) |
| **pytesseract** | Tesseract Python interface |
| **scikit-image** | Haladó képfeldolgozás |

---

## 📊 Hogyan Működik

### Feldolgozási Pipeline

```
[Bemeneti kép]
     ↓
[Szürkeárnyalatos konverzió]
     ↓
[Zaj csökkentés (bilaterális szűrés)]
     ↓
[Éldetektálás (Canny)]
     ↓
[Kontúrok keresése]
     ↓
[Négyszögletű kontúr kiválasztása]
     ↓
[Maszkolás és kivágás]
     ↓
[OCR (Tesseract)]
     ↓
[Felismert rendszáma]
```

---

## 💻 Parancssori Használat

### `main.py` – Egyetlen Kép Feldolgozása

```powershell
python main.py --image <képfájl_elérési_útja> [--verbose]
```

**Paraméterek:**
- `--image` vagy `-i`: Kötelező paraméter (a kép teljes elérési útja)
- `--verbose` vagy `-v`: (opt.) Részletes kimenet (sorszamok is)

**Példák:**
```powershell
python main.py --image "C:\\Users\\kalma\\photo.jpg"
python main.py -i "Képek\\kép.png" -v
```

**Kimenet (egy rendszámozódik):**
```
Felismert rendszám: ABC123
```

**Kimenet (több rendszám):**
```
Felismert 2 rendszám:
  1. ABC123
  2. XYZ789
```

### `batch_scan.py` – Képek Mappájának Feldolgozása

```powershell
python batch_scan.py [--dir <mappa_elérési_útja>]
```

**Paraméterek:**
- `--dir` vagy `-d`: Közzétett könyvtár (alapértelmezett: `Képek`)

**Példák:**
```powershell
python batch_scan.py                    # "Képek" mappra gondol
python batch_scan.py --dir "Képek"
python batch_scan.py -d "C:\myfolder"
```

**Kimenet:**
A mappa összes képéhez kiírja az eredményt:
```
foto1.jpg: ABC1234
foto2.jpg: nincs tábla
foto3.jpg: hiba (nem képfájl)
```

### `image_scanner.py` – Képmetaadatok

```powershell
python image_scanner.py [--path <mappa>]
```

Képek formátumára és méretére vonatkozó adatok.

---

## ⚙️ Konfigurálás

### Támogatott Karakterek

A `main.py` fájlban módosítható:

```python
SUPPORTED_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
```

### OCR Paraméterek

A `recognize_plate()` függvényben:

```python
config = f"--psm 8 --oem 3 -c tessedit_char_whitelist={SUPPORTED_CHARS}"
```

---

## ❌ Szakít Hibaelhárítás

| Hiba | Megoldás |
|------|----------|
| "tesseract is not installed" | Telepítsd a Tesseract OCR motort: [UB-Mannheim link](https://github.com/UB-Mannheim/tesseract/wiki) |
| "No module named 'cv2'" | `pip install opencv-python` |
| "Nem található a kép" | Ellenőrizd az elérési utat és a fájl meglétét |
| "Az OpenCV (cv2) nincs telepítve" | `pip install -r requirements.txt` |

**🔗 Teljes hibaelhárítás: [SETUP.md](SETUP.md#5-hibaelhárítás)**

---

## 📈 Teljesítmény

- **Feldolgozási idő:** ~1-3 másodperc képenként (Tesseract miatt)
- **Memória:** ~100-300 MB működéskor
- **CPU:** Minimális terhelés (OCR a CPU-intenzív)
- **GPU:** Jelenleg nem támogatott

---

## 📝 Támogatott Képformátumok

- ✅ JPEG (`.jpg`, `.jpeg`)
- ✅ PNG (`.png`)
- ✅ BMP (`.bmp`)
- ✅ GIF (`.gif`)
- ✅ TIFF (`.tiff`)

---

## 🎯 Ideális Feltételek

A legjobb eredmény érdekében:

1. **Tiszta, jó kontrasztú kép**
2. **Rendszámtábla a kép középpontjában**
3. **Legalább 100x30 pixel méret**
4. **Well-lit, nem túl zavaros kép**
5. **Egyenes perspektíva (nem szögből fotózva)**

---

## 📄 A projekt a következő feladatra lett készítve

**GKNB_INTM152** – Képfeldolgozás tantárgy

**Feladat:** Rendszámtábla detektálása és leolvasása fényképről.

---

## 📜 Licenc

MIT License – lásd a [LICENSE](LICENSE) fájlt.

---

## 🤝 Hozzájárulás

Kérdések vagy ötletek? Nyugodtan nyiss egy issue-t vagy pull request-et!

---

## 📞 Támogatás

- 📖 **Dokumentáció:** [SETUP.md](SETUP.md)
- 🐛 **Hibajelentés:** GitHub Issues
- 💬 **Kérdés:** Diskusszió szakasz

---

**Köszönjük, hogy használod ezt az alkalmazást!** 🚗✨
