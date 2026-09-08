"""Genera las 31 tarjetas de boleto del wallet y verifica que cada código relea igual."""
import sys, os, io, json, base64; sys.path.insert(0,'.')
from vis import barcodes
from PIL import Image, ImageDraw, ImageFont
import segno

HN='/System/Library/Fonts/HelveticaNeue.ttc'; MENLO='/System/Library/Fonts/Menlo.ttc'
def f(sz,b=False): return ImageFont.truetype(HN, sz, index=1 if b else 0)
def mono(sz,b=False): return ImageFont.truetype(MENLO, sz, index=1 if b else 0)

W = 900
INK='#111111'; MUT='#6B7280'; LINE='#E5E7EB'

def qr_img(payload, px):
    q = segno.make(payload, error='q')
    buf = io.BytesIO(); q.save(buf, kind='png', scale=20, border=2)
    im = Image.open(buf).convert('RGB')
    return im.resize((px, px), Image.NEAREST)

def wrap(draw, txt, font, maxw):
    out, line = [], ''
    for w in txt.split():
        t = (line+' '+w).strip()
        if draw.textlength(t, font=font) <= maxw: line = t
        else: out.append(line); line = w
    if line: out.append(line)
    return out

def card(color, place, when, detail, code_img, code_txt, provider, nth, hi=None):
    """Dibuja en dos pasadas: la primera mide el alto real, la segunda pinta."""
    def render(H, paint):
        im = Image.new('RGB',(W,max(H,10)),'white'); d = ImageDraw.Draw(im)
        if paint: d.rectangle([0,0,W,18], fill=color)          # banda del día
        y = 72
        for txt, fo, col, dy in [(place.upper(), f(46,True), INK, 66), (when, f(32), MUT, 56)]:
            for ln in wrap(d, txt, fo, W-120):
                if paint: d.text((60,y), ln, font=fo, fill=col)
                y += dy
        if nth:
            if paint: d.text((60,y), nth, font=f(30,True), fill=color)
            y += 52
        y += 8
        if paint: d.line([60,y,W-60,y], fill=LINE, width=2)
        y += 46
        side = 520
        if paint: im.paste(code_img.resize((side,side), Image.NEAREST), ((W-side)//2, y))
        y += side + 44
        cf = mono(34,True) if len(code_txt) <= 26 else mono(22,True)
        for ln in wrap(d, code_txt, cf, W-120):
            if paint: d.text(((W-d.textlength(ln,font=cf))//2, y), ln, font=cf, fill=INK)
            y += cf.size + 10
        if hi:
            y += 18
            hf = f(38,True)
            if paint: d.text(((W-d.textlength(hi,font=hf))//2, y), hi, font=hf, fill=color)
            y += 54
        y += 22
        if paint: d.line([60,y,W-60,y], fill=LINE, width=2)
        y += 34
        for ln in wrap(d, detail, f(30), W-120):
            if paint: d.text((60,y), ln, font=f(30), fill=INK)
            y += 42
        y += 30
        if paint: d.text((60,y), provider, font=f(26), fill=MUT)
        y += 34 + 40
        if paint: d.rectangle([0,0,W-1,im.height-1], outline=LINE, width=2)
        return im, y
    _, H = render(10, False)
    im, _ = render(H, True)
    return im

JUE, VIE, SAB = '#EE352E', '#0039A6', '#00933C'
BOM_DET = "Eugene O'Neill Theatre, 230 West 49th St. NYC Broadway Week BOGO, $104.50."
BOM_PROV = 'ATG Tickets · orden 4916404 · jaramillo, emiliano'
SPEC = {
 'est':[dict(color=JUE, place='Estatua de la Libertad', when='Jueves 17 sep · 9:00 AM (seguridad 8:30)',
             detail='Adult Reserve with Pedestal (13–61) × 5. Una sola confirmación para las 5 personas. El ferry no tiene hora: primero en llegar, primero en subir.',
             payload='\\84809333', code_txt='84809333', provider='Statue City Cruises · Castle Clinton, Battery Park', nth=None)],
 'n11':[dict(color=JUE, place='Museo del 9/11', when='Jueves 17 sep · 2:30 PM',
             detail='Fila "Ticket Holder" en la entrada principal, 180 Greenwich St. No hagas fila en taquilla.',
             payload=p, code_txt=p, provider='GetYourGuide · reserva GYG2Q9A47Z5Z', nth=f'Boleto {i} de 5')
        for i,p in enumerate(['040800150001857735','040800150001857736','040800150001857737',
                              '040800150001857738','040800150001857739'],1)],
 'met':[dict(color=VIE, place='MET', when='Viernes 18 sep · desde 10:00 AM',
             hi=t, detail='General Admission. Los estudiantes deben mostrar credencial vigente en la entrada.',
             payload=p, code_txt='#'+p, provider='The Metropolitan Museum of Art · 1000 5th Ave', nth=f'Boleto {i} de 5')
        for i,(p,t) in enumerate([('68024765','Adult Admission · $30.00'),('68024764','Student Admission · $17.00'),
                                  ('68024763','Student Admission · $17.00'),('68024762','Student Admission · $17.00'),
                                  ('68024761','Student Admission · $17.00')],1)],
 'amnh':[dict(color=VIE, place='Museo de Historia Natural', when='Viernes 18 sep · 2:30 PM',
              detail='Entrada general. Los 4 estudiantes llevan credencial: aquí también la piden.',
              payload=p, code_txt=p, provider='American Museum of Natural History · Central Park West', nth=f'Boleto {i} de 5')
         for i,p in enumerate(['91283416','91283417','91283418','91283419','91283420'],1)],
 'moma':[dict(color=SAB, place='MoMA', when='Sábado 19 sep · desde 10:30 AM',
              detail='Entrada con horario. 11 W 53rd St, a 10 min a pie del hotel.',
              payload=p, code_txt=p.split('"')[-2], provider='Museum of Modern Art · orden 111577105', nth=f'Boleto {i} de 5')
         for i,p in enumerate(['{"ver":2,"uuid":"at1a6eb0-f3a1f54e01a41c655f-d874316f"}',
                               '{"ver":2,"uuid":"atdb0f10-95420746cca5004062-46d5232d"}',
                               '{"ver":2,"uuid":"at95d2c8-bebd994d0aa7c394bd-4c17124c"}',
                               '{"ver":2,"uuid":"at8557fa-a939984841acc0d8e1-2a105bf2"}',
                               '{"ver":2,"uuid":"at7c74dd-ff8bea427aa9e01969-3c66815b"}'],1)],
 'summit':[dict(color=SAB, place='Summit One Vanderbilt', when='Sábado 19 sep · 5:30 PM',
                detail='SUMMIT ASCENT · Adult · Entry + Ascent. 45 E 42nd St, junto a Grand Central.',
                payload=p, code_txt=p, provider='SUMMIT One Vanderbilt · orden 49431400', nth=f'Boleto {i} de 5')
           for i,p in enumerate(['1002011050359449576027','1002011050359394763160','1002011050359357496597',
                                 '1002011050359437114834','1002011050359383613679'],1)],
 'bom':[dict(color=VIE, place='The Book of Mormon', when='Viernes 18 sep · 7:00 PM',
             hi=seat, detail=det,
             dm=f'dm_{i}.png', code_txt=p, provider=prov, nth=f'Boleto {i+1} de 6')
        for i,(p,seat,det,prov) in enumerate([
            ('41831440349','Orchestra Left C 9',  BOM_DET, BOM_PROV),
            ('41831995226','Orchestra Left C 11', BOM_DET, BOM_PROV),
            ('41832272373','Orchestra Left C 13', BOM_DET, BOM_PROV),
            ('41831744220','Orchestra Left E 13', BOM_DET, BOM_PROV),
            ('41831451168','Orchestra Left E 15', BOM_DET, BOM_PROV),
            ('41831797527','Orchestra Left E 21',
             "VISTA PARCIAL: el boleto dice Partial View, se ve parte del escenario tapada. "
             "Eugene O'Neill Theatre, 230 West 49th St. Tarifa regular, $149.00.",
             'ATG Tickets · orden 4937619 · el sexto boleto, comprado aparte'),
        ])],
}

TIX = {}; fails = []
for key, specs in SPEC.items():
    TIX[key] = []
    for s in specs:
        if 'dm' in s:
            img = Image.open(s['dm']).convert('RGB'); expect = s['code_txt']
        else:
            img = qr_img(s['payload'], 520); expect = s['payload']
        c = card(s['color'], s['place'], s['when'], s['detail'], img, s['code_txt'], s['provider'], s['nth'], s.get('hi'))
        got = barcodes(c)
        ok = any(b['payload'] == expect for b in got)
        print(f"{key:7} {expect[:34]:36} {'OK' if ok else 'FALLA -> '+str([b['payload'] for b in got])}")
        if not ok: fails.append((key, expect))
        buf = io.BytesIO(); c.quantize(colors=16, method=Image.MEDIANCUT).save(buf, 'PNG', optimize=True)
        TIX[key].append(base64.b64encode(buf.getvalue()).decode())
        c.save(f'card_{key}_{len(TIX[key])}.png')
        assert barcodes(Image.open(io.BytesIO(buf.getvalue())).convert('RGB')), 'el PNG comprimido no relee'

print('\nfallas:', fails)
json.dump(TIX, open('TIX_new.json','w'))
print('tarjetas:', sum(len(v) for v in TIX.values()), '· peso base64:', sum(len(x) for v in TIX.values() for x in v)//1024, 'KB')
