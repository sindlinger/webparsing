from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import subprocess
import httpx
import json
import os

app = FastAPI(
    title="Document Processing API",
    description="API para processamento de documentos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Diretórios
UPLOAD_DIR = Path("document_processor/uploads")
RESULTS_DIR = Path("document_processor/results")

for dir_path in [UPLOAD_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...), services: str = '[]'):
    services_list = json.loads(services)
    file_path = UPLOAD_DIR / file.filename
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Integração com Tika
        if 'tika' in services_list:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    "http://tika:9998/tika", 
                    files={"upload": (file.filename, open(file_path, "rb"), file.content_type)}
                )
                # Manipula a resposta do Tika

        # Integração com SpaCy
        if 'spacy' in services_list:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "http://spacy:8080/process",
                    files={"file": (file_path.name, open(file_path, "rb"))}
                )
                # Manipula a resposta do SpaCy

        # Processamento OCRmyPDF
        if 'ocrmypdf' in services_list and file_path.suffix == '.pdf':
            ocr_output_path = RESULTS_DIR / f"ocr_{file.filename}"
            command = [
                "docker", "run", "--rm",
                "-v", f"{UPLOAD_DIR.resolve()}:/input",
                "-v", f"{RESULTS_DIR.resolve()}:/output",
                "jbarlow83/ocrmypdf",
                f"/input/{file.filename}", f"/output/ocr_{file.filename}"
            ]
            result = subprocess.run(command, capture_output=True, text=True)
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail=f"OCR error: {result.stderr}")

        return {
            "status": "success",
            "message": "Processamento concluído com sucesso.",
            "services_used": services_list
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "Document Processing API is running"}

@app.get("/status")
async def status():
    return {
        "status": "online",
        "directories": {
            "uploads": UPLOAD_DIR.exists(),
            "results": RESULTS_DIR.exists()
        }
    }

@app.get("/files/")
async def list_files():
    uploads = [f.name for f in UPLOAD_DIR.glob("*") if f.is_file()]
    results = [f.name for f in RESULTS_DIR.glob("*") if f.is_file()]

    return {
        "uploads": uploads,
        "results": results
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)