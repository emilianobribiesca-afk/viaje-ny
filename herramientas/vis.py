import sys, io, json
import Vision, Quartz
from Foundation import NSData
from PIL import Image

def _handler_from_pil(im):
    buf = io.BytesIO(); im.convert('RGB').save(buf, 'PNG')
    data = NSData.dataWithBytes_length_(buf.getvalue(), len(buf.getvalue()))
    return Vision.VNImageRequestHandler.alloc().initWithData_options_(data, None)

def barcodes(im):
    h = _handler_from_pil(im)
    req = Vision.VNDetectBarcodesRequest.alloc().init()
    ok, err = h.performRequests_error_([req], None)
    out = []
    for r in (req.results() or []):
        out.append({'sym': str(r.symbology()), 'payload': r.payloadStringValue(),
                    'bbox': tuple(round(x,4) for x in (r.boundingBox().origin.x, r.boundingBox().origin.y,
                                  r.boundingBox().size.width, r.boundingBox().size.height))})
    return out

def text(im):
    h = _handler_from_pil(im)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(1)  # accurate=0? 0 accurate,1 fast -> use 0
    req.setRecognitionLevel_(0)
    req.setUsesLanguageCorrection_(False)
    h.performRequests_error_([req], None)
    lines = []
    for r in (req.results() or []):
        c = r.topCandidates_(1)
        if c and len(c): lines.append(str(c[0].string()))
    return lines
