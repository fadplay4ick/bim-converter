from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import zipfile
import io
import re

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

def clean_text(text):
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text

@app.post("/convert")
async def convert_file(request: Request, file: UploadFile = File(None)):
    if file and file.filename:
        content = await file.read()
        filename = file.filename
    else:
        content = await request.body()
        filename = request.headers.get("X-Filename", "file.txt")

    text = ""

    if filename.endswith(".ifc"):
        text = clean_text(content.decode("utf-8", errors="ignore"))
    elif filename.endswith(".bcfzip"):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                parts = []
                for name in z.namelist():
                    if name.endswith(".bcf") or name.endswith(".xml"):
                        raw = z.read(name).decode("utf-8", errors="ignore")
                        parts.append(f"== {name} ==\n{clean_text(raw)}")
                text = "\n\n".join(parts)
        except Exception as e:
            text = f"Error: {str(e)}"
    else:
        text = clean_text(content.decode("utf-8", errors="ignore"))

    return JSONResponse({"text": text, "fileName": filename})
