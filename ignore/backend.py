from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import httpx
import aiofiles
import asyncio
import logging
import os
import json
from datetime import datetime
import PyPDF2
import pytesseract
from PIL import Image
import spacy
import requests
from pathlib import Path
import hashlib
import aiohttp
import io

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Modelos Pydantic para validação
class ProcessingRequest(BaseModel):
    services: List[str]
    options: Optional[Dict] = {}

class ProcessingResponse(BaseModel):
    task_id: str
    status: str
    results: Optional[Dict] = None
    error: Optional[str] = None

# Configuração da aplicação FastAPI
app = FastAPI(title="Document Processing Service")

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especifique os domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações
UPLOAD_DIR = Path("uploads")
RESULTS_DIR = Path("results")
OLLAMA_URL = "http://localhost:11434"
TIKA_URL = "http://localhost:9998"
SPACY_URL = "http://localhost:8080"

# Criar diretórios necessários
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Classe para gerenciar o processamento de documentos
class DocumentProcessor:
    def __init__(self):
        self.tasks = {}
        self.nlp = spacy.load("en_core_web_sm")
    
    async def process_with_ollama(self, text: str, model: str = "llama2") -> Dict:
        """Processa texto usando Ollama."""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={
                        "model": model,
                        "prompt": f"Analyze the following text and provide a summary, key entities, and main topics:\n\n{text}",
                        "stream": False
                    }
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Error processing with Ollama: {e}")
                return {"error": str(e)}

    async def extract_text_tika(self, file_path: Path) -> str:
        """Extrai texto usando Apache Tika."""
        async with aiofiles.open(file_path, 'rb') as f:
            file_data = await f.read()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.put(
                    f"{TIKA_URL}/tika",
                    content=file_data,
                    headers={'Accept': 'text/plain'}
                )
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"Error extracting text with Tika: {e}")
                return ""

    async def process_with_spacy(self, text: str) -> Dict:
        """Processa texto usando SpaCy para NER e análise sintática."""
        doc = self.nlp(text)
        entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
        sentences = [sent.text for sent in doc.sents]
        return {
            "entities": entities,
            "sentences": sentences,
            "tokens": [token.text for token in doc]
        }

    async def perform_ocr(self, image_path: Path) -> str:
        """Realiza OCR em uma imagem."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"Error performing OCR: {e}")
            return ""

    async def process_document(self, file_path: Path, services: List[str], options: Dict) -> Dict:
        """Processa um documento usando os serviços selecionados."""
        results = {}
        
        # Extrair texto do documento
        text = await self.extract_text_tika(file_path)
        
        # Processar com diferentes serviços
        tasks = []
        
        if "haystack" in services:
            tasks.append(self.process_with_ollama(text))
        
        if "spacy" in services:
            results["spacy"] = await self.process_with_spacy(text)
        
        if "ocr" in services and file_path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            results["ocr"] = await self.perform_ocr(file_path)
        
        # Aguardar resultados assíncronos
        if tasks:
            completed_tasks = await asyncio.gather(*tasks)
            for i, service in enumerate(["haystack"]):
                if service in services:
                    results[service] = completed_tasks[i]
        
        return results

# Instância do processador de documentos
processor = DocumentProcessor()

@app.post("/api/process", response_model=ProcessingResponse)
async def process_document(
    file: UploadFile = File(...),
    request: ProcessingRequest = None,
    background_tasks: BackgroundTasks = None
):
    """Endpoint para processar documentos."""
    try:
        # Gerar ID único para a tarefa
        task_id = hashlib.md5(f"{file.filename}{datetime.now()}".encode()).hexdigest()
        
        # Salvar arquivo
        file_path = UPLOAD_DIR / f"{task_id}_{file.filename}"
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Iniciar processamento em background
        background_tasks.add_task(
            process_and_save_results,
            task_id,
            file_path,
            request.services,
            request.options
        )
        
        return ProcessingResponse(
            task_id=task_id,
            status="processing"
        )
    
    except Exception as e:
        logger.error(f"Error processing document: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def process_and_save_results(task_id: str, file_path: Path, services: List[str], options: Dict):
    """Processa documento e salva resultados."""
    try:
        results = await processor.process_document(file_path, services, options)
        
        # Salvar resultados
        results_path = RESULTS_DIR / f"{task_id}.json"
        async with aiofiles.open(results_path, 'w') as f:
            await f.write(json.dumps(results))
        
        processor.tasks[task_id] = {
            "status": "completed",
            "results": results
        }
    
    except Exception as e:
        logger.error(f"Error processing task {task_id}: {e}")
        processor.tasks[task_id] = {
            "status": "failed",
            "error": str(e)
        }
    
    finally:
        # Limpar arquivo temporário
        if file_path.exists():
            file_path.unlink()

@app.get("/api/status/{task_id}", response_model=ProcessingResponse)
async def get_task_status(task_id: str):
    """Verifica o status de uma tarefa de processamento."""
    if task_id not in processor.tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = processor.tasks[task_id]
    return ProcessingResponse(
        task_id=task_id,
        status=task["status"],
        results=task.get("results"),
        error=task.get("error")
    )

@app.get("/api/health")
async def health_check():
    """Endpoint de verificação de saúde do serviço."""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)