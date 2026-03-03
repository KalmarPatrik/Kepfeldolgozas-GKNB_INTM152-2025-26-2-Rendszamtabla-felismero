# Gyors Referencia

## Indulás 30 másodperc alatt

```powershell
# 1. Virtual environment
python -m venv .venv
./.venv/Scripts/Activate.ps1

# 2. Csomagok telepítése
pip install -r requirements.txt

# 3. Tesseract telepítése
# Letöltés: https://github.com/UB-Mannheim/tesseract/wiki

# 4. Futtatás!
python main.py -i "photo.jpg"
```

---

## Parancsok

| Feladat | Parancs |
|--------|---------|
| **Egyetlen kép** | `python main.py -i "image.jpg"` |
| **Egyetlen kép (verbos)** | `python main.py -i "image.jpg" -v` |
| **Képek mappa** | `python batch_scan.py` |
| **Más mappa** | `python batch_scan.py --dir "C:\images"` |
| **Venv kilépés** | `deactivate` |

---

## Kimeneti Formátumok

### main.py - Egy rendszám:
```
Felismert rendszám: ABC123
```

### main.py - Több rendszám:
```
Felismert 2 rendszám:
  1. ABC123
  2. XYZ789
```

### main.py - Verbose módban (-v):
```
Felismert 2 rendszám:
  1. ABC123
  2. XYZ789
```

### batch_scan.py:
```
[OK] photo.jpg:
   1. ABC123
   2. XYZ789

[-] photo2.jpg: nincs tábla

[!] bad.jpg: hiba (can't open file)

=== Feldolgozás kész ===
Feldolgozva: 9 kép
Talált rendszámok: 3
Hibás: 0
```

---

## Fontosabb Koncepciók

### Több Rendszám Felismerése
- A program automatikusan több rendszámtáblát talál meg egy képen
- Bal-jobb szerinti sorrendben vannak sorszámozva
- Valódiság-szűrés: csak érvényes rendszámokat mutat

### Valódiság Kritériumok
- **Forma:** Négyszögletű kell lenni
- **Arány:** 1.5:1 - 6:1 közötti hosszúsági/magassági arány
- **Szöveg:** 3-7 alfanumerikus karakter, legalább 1 betű és 1 szám
- **Rendezés:** Képen balról jobbra (pozíció szerinti)

---

## Hibamegoldás

| Hiba | Megoldás |
|------|----------|
| "tesseract is not installed" | Telepítsd: https://github.com/UB-Mannheim/tesseract/wiki |
| "No module named 'cv2'" | `pip install opencv-python` |
| "Nem található a kép" | Használj teljes elérési útat |
| Unicode hiba | Használj UTF-8 kódolást |

---

## Tippek

1. **Lassú feldolgozás?** Ez normális, OCR erőforrátigényes (~1-3 mp/kép)
2. **Rossz felismerés?** Tiszta, nagy kontrasztú képeket használ
3. **Több kép?** batch_scan.py gyorsabb
4. **Saját karakterek?** SUPPORTED_CHARS módosítása

---

## Fájlszerkezet

```
projekt/
├── main.py                    # Fő program
├── batch_scan.py              # Kötegelt feldolgozás
├── image_scanner.py           # Kép-metaadat olvasó
├── requirements.txt           # Python függőségek
├── README.md                  # Teljes dokumentáció
├── SETUP.md                   # Telepítési útmutató
├── QUICKREF.md                # Ez a fájl
└── Képek/                     # Bemenet képek
    ├── photo1.jpg
    ├── photo2.jpg
    └── ...
```

---

**További help: SETUP.md vagy README.md!**
