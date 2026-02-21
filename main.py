from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
import zipfile
import io
import re
import xml.etree.ElementTree as ET

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "ok"}

def clean_text(text):
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
    return text

def parse_xml_to_text(xml_string):
    try:
        root = ET.fromstring(xml_string)
        texts = []
        for elem in root.iter():
            if elem.text and elem.text.strip():
                texts.append(f"{elem.tag}: {elem.text.strip()}")
            if elem.attrib:
                for k, v in elem.attrib.items():
                    texts.append(f"{elem.tag}.{k}: {v}")
        return "\n".join(texts)
    except:
        return clean_text(xml_string)

@app.post("/convert")
async def convert_file(file: UploadFile = File(None), request: Request = None):
    if file is None:
        content = await request.body()
        filename = "file.txt"
    else:
        content = await file.read()
        filename = file.filename or "file.txt"

    text = ""

    if filename.endswith(".ifc"):
        text = clean_text(content.decode("utf-8", errors="ignore"))
    elif filename.endswith(".bcfzip"):
        try:
            buf = io.BytesIO(content)
            with zipfile.ZipFile(buf) as z:
                parts = []
                for name in z.namelist():
                    if name.endswith(".bcf") or name.endswith(".xml"):
                        raw = z.read(name).decode("utf-8", errors="ignore")
                        parsed = parse_xml_to_text(raw)
                        parts.append(f"== {name} ==\n{parsed}")
                text = "\n\n".join(parts)
        except Exception as e:
            text = f"Error: {str(e)}"
    else:
        text = clean_text(content.decode("utf-8", errors="ignore"))

    return JSONResponse(content={"text": text, "fileName": filename}, media_type="application/json")
