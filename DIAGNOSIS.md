# Diagnózis és Fejlesztési Irányok (2026-03-11)

## Jelenlegi helyzet

A projekt fő funkciói működnek, de a felismerési minőség képtől függően változó.
A pipeline jelenleg klasszikus CV + Tesseract OCR alapú, szabályalapú utópontozással.

## Erősségek

- Több forrásból gyűjt régiójelölteket (`edge`, `blackhat`, `adaptive`).
- Perspektívakorrekciót alkalmaz a kivágásokon.
- Több OCR variánst és PSM módot próbál.
- Magyar rendszámformátumokra szabályalapú normalizálást használ.
- Több találatot deduplikál és balról jobbra rendez.

## Korlátok

- OCR bizonytalanság gyenge minőségű vagy dőlt képeken.
- Teljes benchmark futtatás időigényes lehet.
- Ritka/tört karaktereknél még előfordulhat hamis pozitív vagy hamis negatív.

## Rövid távú fejlesztési javaslatok

1. Operatív javítások
- OCR timeout és PSM finomhangolás képkészlet alapján.
- További normalizáló szabályok a gyakori tévesztésekre.

2. Mérhetőség
- Benchmark eredmény mentés UTF-8-ban minden futásnál.
- Külön metrikák: képszintű pontosság, táblaszintű recall.

3. Robusztusság
- Opcionális előszűrés gyenge minőségű kivágásokra.
- Kiterjesztett fallback minták validációval.

## Középtávú javaslat

- OCR motor összehasonlítás (Tesseract vs EasyOCR/PaddleOCR) ugyanazon kivágásokon.
- Esetleges hibrid stratégia: klasszikus detektálás + modernebb OCR.

## Konzultációs fókusz

- Miért választottuk a mostani baseline pipeline-t.
- Mely pontokon a legnagyobb a nyereség (OCR csere vagy bővítés).
- Hogyan tudjuk objektíven mérni a javulást (benchmark protokoll).
