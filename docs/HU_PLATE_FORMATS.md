# Magyar Rendszámformátumok

Ez a projekt a 326/2011. (XII. 28.) Korm. rendelet jelenleg hatályos szabályai alapján a következő formátumokat veszi figyelembe.

## Állandó rendszámtáblák

- 1990 utáni, 2004 előtti és a 2004-es sorozatformátum karakterkiosztása: 3 betű + 3 számjegy.
- 2022. július 1-től kiadott általános sorozatformátum: 2 betű + címer + 2 betű + kötőjel + 3 számjegy.
- A B, C és E típusú táblák fizikai kialakításuk miatt nem tartalmaznak kötőjelet, de az OCR normalizálva kötőjeles alakban adja vissza.
- 2022-től az egyedileg előállított állandó rendszám legalább 3, legfeljebb 6 betűből és legalább 1, legfeljebb 4 számjegyből állhat, összesen 7 karakterrel.

## Különleges rendszámtáblák

- 2022-től a CD, OT, TX, BA, HA, MA, NA és RA előtagú különleges rendszámok a prefix után 2 betűt és 3 számjegyet tartalmaznak.
- A környezetkímélő járművek világoszöld alapszínűek, de a karakterkiosztás az alapformátumot követi.
- A kerékpárszállító eszköz rendszáma a hordozó jármű karakterkiosztását követi, címer nélkül.

## Ideiglenes rendszámtáblák

- A 2022-től kiadott fekete karakteres I rendszám: I + 2 számjegy + 2 betű + a kiadás évének utolsó 2 számjegye.
- A piros karakteres I rendszám: I + 3 számjegy + kötőjel + 2 betű.
- A 2025. február 1-től kiadott speciális piros I rendszám végződése SP, SO, SR vagy ST.
- A 2022-től kiadott ideiglenes CD rendszám: CD + 4 számjegy + a kiadás évének utolsó 2 számjegye.
- A korábbi ideiglenes SP rendszám: SP + 4 számjegy.
- A korábbi M rendszám: M + 6 számjegy.
- A korábbi Z, P, E és V rendszámok: prefix + 5 számjegy, bizonyos esetekben a kiadási év utolsó két számjegyével kiegészítve.

## Megjegyzés az OCR normalizálásról

- A rendszer az OCR-ben a címer helyét vizuálisan nem kezeli külön karakterként, ezért a 2022-es állandó rendszámokat normalizált szövegként például AA-AB-123 alakban adja vissza.
- A színinformáció a szürkeárnyalatos OCR-ben nem mindig használható stabilan, ezért az elfogadás elsődlegesen karakterkiosztás alapján történik.
- A repo referenciahalmazában szerepel egy olyan mintakép is, amely nem illeszkedik teljesen a mai szigorú jogszabályi sablonokhoz; erre a rendszer alacsony prioritású kompatibilitási fallbacket tart fenn.