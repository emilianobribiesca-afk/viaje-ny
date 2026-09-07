"""Recorta el DataMatrix de cada página de tickets.pdf a alta resolución."""
import sys, os, io; sys.path.insert(0,'.')
from vis import barcodes
from PIL import Image
import fitz

src = os.path.expanduser('~/Downloads/tickets.pdf')
doc = fitz.open(src)
out = []
for i, pg in enumerate(doc):
    hi = Image.open(io.BytesIO(pg.get_pixmap(dpi=600).tobytes('png')))
    lo = Image.open(io.BytesIO(pg.get_pixmap(dpi=200).tobytes('png')))
    bc = barcodes(lo)
    assert len(bc) == 1, (i, bc)
    x, y, w, h = bc[0]['bbox']          # normalizado, origen abajo-izquierda
    W, H = hi.size
    pad = 0.06
    L = int((x - w*pad) * W); R = int((x + w*(1+pad)) * W)
    T = int((1 - y - h*(1+pad)) * H); B = int((1 - y + h*pad) * H)
    crop = hi.crop((max(0,L), max(0,T), min(W,R), min(H,B)))
    # cuadrar sobre blanco
    side = max(crop.size)
    sq = Image.new('RGB', (side, side), 'white')
    sq.paste(crop, ((side-crop.width)//2, (side-crop.height)//2))
    f = f'dm_{i}.png'; sq.save(f)
    chk = barcodes(sq)
    ok = chk and chk[0]['payload'] == bc[0]['payload']
    print(f'{f} {sq.size} payload={bc[0]["payload"]} recorte-relee={"OK" if ok else "FALLA "+str(chk)}')
    out.append((f, bc[0]['payload']))
