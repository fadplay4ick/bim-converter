from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import zipfile
import io

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/convert")
async def convert_file(file: UploadFile = File(None), request: Request = None):
    if file is None:
        body = await request.body()
        content = body
        filename = "file.txt"
    else:
        content = await file.read()
        filename = file.filename or "file.txt"
    
    text = ""

    if filename.endswith(".ifc"):
        text = content.decode("utf-8", errors="ignore")
    elif filename.endswith(".bcfzip"):
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as z:
                parts = []
                for name in z.namelist():
                    if name.endswith(".bcf") or name.endswith(".xml"):
                        parts.append(f"== {name} ==\n{z.read(name).decode('utf-8', errors='ignore')}")
                text = "\n\n".join(parts)
                text = text.encode('utf-8', errors='ignore').decode('utf-8')
                text = text.replace('\x00', '')
        except Exception as e:
            text = f"Error reading bcfzip: {str(e)}"
    else:
        text = content.decode("utf-8", errors="ignore")

    return JSONResponse({"text": text, "fileName": filename})
