# Gyors Referencia

## 30 másodperces indulás

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Ha tiltott script futtatás hiba van:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

pip install -r requirements.txt
python main.py -i "Képek\images.jpg"
```

## Parancsok

| Feladat | Parancs |
|---|---|
| Egy kép | `python main.py -i "image.jpg"` |
| Egy kép, részletes | `python main.py -i "image.jpg" -v` |
| Képmappa | `python batch_scan.py` |
| Más mappa | `python batch_scan.py -d "C:\images"` |
| Benchmark | `python benchmark.py` |
| Aktiválás nélkül | `.\.venv\Scripts\python.exe main.py -i "image.jpg"` |
| Venv kilépés | `deactivate` |

## Kimenet minták

```text
Felismert rendszám: AA-AB-123
```

```text
[OK] photo.jpg:
   1. AA-AB-123
[-] photo2.jpg: nincs tábla
[!] bad.jpg: hiba (...)

=== Feldolgozás kész ===
Feldolgozva: 9 kép
Talált rendszámok: 3
Hibás: 0
```

## Mit csinál a projekt

- Több rendszámot is keres egy képen.
- A találatokat balról jobbra rendezi.
- Formátum-alapú pontozással csökkenti a hamis pozitívokat.

## Gyors hibakeresés

| Hiba | Megoldás |
|---|---|
| `running scripts is disabled` | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `No module named 'cv2'` | `pip install -r requirements.txt` |
| `tesseract is not installed` | Tesseract telepítés: UB Mannheim oldal |
| Kép nem nyitható | Ellenőrizd az útvonalat, használj abszolút path-t |

## Fájlok

```text
main.py
batch_scan.py
benchmark.py
requirements.txt
README.md
SETUP.md
TECHNICAL.md
SUMMARY.md
DIAGNOSIS.md
Képek/
```
