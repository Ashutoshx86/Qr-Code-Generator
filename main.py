from pathlib import Path
from io import BytesIO

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel
import qrcode

app = FastAPI(title="QR Code Generator API")

INDEX_FILE = Path(__file__).parent / "static" / "index.html"


class QRRequest(BaseModel):
    text: str
    color: str = "#000000"   
    size: int = 10           

@app.get("/")
def home():
    return FileResponse(INDEX_FILE)


@app.post("/generate-qr")
def generate_qr(req: QRRequest):
    text = req.text.strip()

    if text == "":
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    if len(text) > 500:
        raise HTTPException(status_code=400, detail="Text too long (max 500 characters)")

    if req.size < 1 or req.size > 30:
        raise HTTPException(status_code=400, detail="Size must be between 1 and 30")

    qr = qrcode.QRCode(box_size=req.size, border=4)
    qr.add_data(text)
    qr.make(fit=True)

    try:
        img = qr.make_image(fill_color=req.color, back_color="white")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid color")

    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return Response(
        content=buffer.getvalue(),
        media_type="image/png",
        headers={"Content-Disposition": 'inline; filename="qrcode.png"'},
    )