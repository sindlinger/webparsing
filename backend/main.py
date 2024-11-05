from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import httpx
import subprocess
import json
import os
import logging
import pytesseract
from pdf2image import convert_from_path

# Configuração de logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

# CORS
origins = ["http://localhost:3000", "http://localhost:3001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configurações dos serviços usando nomes dos containers
TIKA_URL = "http://tika:9998"
SPACY_URL = "http://spacy:80"

# Diretórios
BASE_DIR = Path(__file__).parent
UPLOAD_DIR = BASE_DIR / "document_processor/uploads"
RESULTS_DIR = BASE_DIR / "document_processor/results"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

def extract_text_from_pdf(pdf_path: Path) -> str:
    """
    Extrai texto de um PDF usando OCR
    """
    try:
        # Converte PDF para imagens
        images = convert_from_path(pdf_path)
        
        # Extrai texto de cada página
        text = ""
        for i, image in enumerate(images):
            # Extrai texto da imagem usando tesseract
            page_text = pytesseract.image_to_string(image, lang='por')
            text += f"\n--- Página {i+1} ---\n{page_text}\n"
            
        return text
    except Exception as e:
        logger.error(f"Erro ao extrair texto: {str(e)}")
        return ""

async def test_tika():
    """Testa conexão com Tika"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{TIKA_URL}/version")
            logger.info(f"Tika version response: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Tika test error: {str(e)}")
        return False

async def test_spacy():
    """Testa conexão com SpaCy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{SPACY_URL}/")
            logger.info(f"SpaCy test response: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"SpaCy test error: {str(e)}")
        return False

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    services: str = Form(...)
):
    """Processa arquivo com os serviços selecionados"""
    try:
        services_list = json.loads(services)
        logger.info(f"Serviços recebidos: {services_list}")
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar services JSON: {e}")
        raise HTTPException(status_code=400, detail="Invalid services format")
    
    safe_filename = "".join(c if c.isalnum() or c in ".-_" else "_" for c in file.filename)
    file_path = UPLOAD_DIR / safe_filename
    results = {}
    
    logger.info(f"Recebendo arquivo: {file.filename}")
    logger.info(f"Nome sanitizado: {safe_filename}")
    logger.info(f"Serviços solicitados: {services_list}")

    try:
        # Ler e salvar arquivo
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        logger.info(f"Arquivo salvo em: {file_path}")

        # Processar com Tika
        if 'tika' in services_list:
            try:
                logger.debug("Iniciando processamento Tika")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.put(
                        f"{TIKA_URL}/tika",
                        content=content,
                        headers={
                            "Accept": "text/plain",
                            "Content-Type": file.content_type or "application/octet-stream"
                        }
                    )
                    response.raise_for_status()
                    results['tika'] = {"text": response.text}
                    logger.info("Processamento Tika concluído")
            except Exception as e:
                logger.error(f"Erro Tika: {str(e)}")
                results['tika'] = {"error": str(e)}

        # Processar com SpaCy
        if 'spacy' in services_list:
            try:
                logger.debug("Iniciando processamento SpaCy")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        f"{SPACY_URL}/process",
                        files={"file": (file.filename, content)}
                    )
                    response.raise_for_status()
                    results['spacy'] = response.json()
                    logger.info("Processamento SpaCy concluído")
            except Exception as e:
                logger.error(f"Erro SpaCy: {str(e)}")
                results['spacy'] = {"error": str(e)}

        # Processar com OCR
        if 'ocrmypdf' in services_list and file_path.suffix.lower() == '.pdf':
            try:
                logger.debug("Iniciando processamento OCR")
                
                # Extrair texto diretamente do PDF
                extracted_text = extract_text_from_pdf(file_path)
                
                # Salvar o texto em um arquivo
                text_output_path = RESULTS_DIR / f"{safe_filename}_texto.txt"
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                
                results['ocrmypdf'] = {
                    'status': 'success',
                    'text_content': extracted_text,
                    'text_file': str(text_output_path)
                }
                logger.info("Processamento OCR e extração de texto concluídos")
                    
            except Exception as e:
                logger.error(f"Erro OCR: {str(e)}")
                results['ocrmypdf'] = {"error": str(e)}

        return {
            "status": "success",
            "message": "Processamento concluído com sucesso",
            "results": results,
            "services_used": services_list
        }

    except Exception as e:
        logger.error(f"Erro geral: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))