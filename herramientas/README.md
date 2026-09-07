# Generador del wallet de boletos

Rehace las 31 tarjetas de `TIX` y las inyecta en `index.html`. Úsalo cuando cambie
un boleto; no edites el base64 a mano.

```
python3 crop_dm.py    # recorta los DataMatrix de ~/Downloads/tickets.pdf (Book of Mormon)
python3 cards.py      # genera las 31 tarjetas -> TIX_new.json, verifica cada código
python3 inject.py     # mete TIX en el maestro y en ../index.html (deja .bak)
```

- `vis.py` — Vision de macOS (pyobjc): decodifica códigos y OCR.
- Cada tarjeta se re-decodifica **desde el PNG ya comprimido**: si un código no relee
  igual que el original, el script lo reporta y `cards.py` falla el assert.
- Los QR se regeneran con `segno` desde el payload exacto. Los DataMatrix no se
  regeneran (no hay generador en la Mac): se recortan a 600 dpi del PDF original.
- Cecconi's queda como captura: es la única reserva sin código escaneable.
- Fuentes de verdad: `~/Downloads/` — `tickets.pdf` (BoM), `TicketOrder20260904-49431400.pdf`
  (Summit), `Print Tickets | The Metropolitan Museum of Art.pdf` (MET),
  `91CG28ZLV26Y3B3HWTC1EBUFUE1T75L2.pdf` (9/11), `IMG_7277.PNG` (Estatua),
  `IMG_7280–7282.PNG` (AMNH), `IMG_7283–7287.PNG` (MoMA).

Tras publicar, sube la versión de `CACHE` en `sw.js`: el service worker es
cache-first y sin bump los celulares que ya instalaron la PWA siguen viendo la
versión vieja.
