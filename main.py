from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
import zipfile
import io

app = FastAPI()

@app.post("/convert")
async def convert_file(file: UploadFile = File(...)):
    content = await file.read()
    filename = file.filename
    text = ""

    if filename.endswith(".ifc"):
        text = content.decode("utf-8", errors="ignore")

    elif filename.endswith(".bcfzip"):
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            parts = []
            for name in z.namelist():
                if name.endswith(".bcf") or name.endswith(".xml"):
                    parts.append(f"== {name} ==\n{z.read(name).decode('utf-8', errors='ignore')}")
            text = "\n\n".join(parts)

    elif filename.endswith(".txt") or filename.endswith(".json"):
        text = content.decode("utf-8", errors="ignore")

    else:
        text = content.decode("utf-8", errors="ignore")

    return JSONResponse({"text": text, "fileName": filename})
```

---

**Файл 2 — `requirements.txt`**
```
fastapi
uvicorn
python-multipart
```

---

**Файл 3 — `Procfile`**
```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
