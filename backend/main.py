from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os

app = FastAPI(
    title="Document Processing API",
    description="API para processamento de documentos",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Definir diretórios
UPLOAD_DIR = Path("document_processor/uploads")
RESULTS_DIR = Path("document_processor/results")
LOGS_DIR = Path("document_processor/logs")

# Garantir que os diretórios existam
for dir_path in [UPLOAD_DIR, RESULTS_DIR, LOGS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Document Processing API is running"}

@app.get("/status")
async def status():
    return {
        "status": "online",
        "directories": {
            "uploads": UPLOAD_DIR.exists(),
            "results": RESULTS_DIR.exists(),
            "logs": LOGS_DIR.exists()
        }
    }

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "filename": file.filename,
            "status": "success",
            "message": "File uploaded successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
