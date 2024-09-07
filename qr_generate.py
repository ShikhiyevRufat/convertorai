import pyqrcode
import io

def qr_generate(text: str):
    url = pyqrcode.create(text) 
    buffer = io.BytesIO()
    url.png(buffer, scale=8) 
    buffer.seek(0)
    
    return buffer.getvalue()
