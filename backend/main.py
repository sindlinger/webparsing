from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
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

# Configurações dos serviços usando portas mapeadas dos containers
TIKA_URL = "http://localhost:9998"
SPACY_URL = "http://localhost:8080"

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

async def process_with_spacy(content: bytes, filename: str):
    """
    Processa conteúdo com SpaCy usando o endpoint /ent para NER
    """
    try:
        # Primeiro extrai o texto usando Tika
        async with httpx.AsyncClient(timeout=30.0) as client:
            tika_response = await client.put(
                f"{TIKA_URL}/tika",
                content=content,
                headers={
                    "Accept": "text/plain; charset=utf-8"
                }
            )
            text_content = tika_response.text
            logger.debug(f"Texto extraído do Tika: {text_content[:200]}...")

        # Processa o texto com SpaCy para extração de entidades
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{SPACY_URL}/ent",  # Usando endpoint de entidades
                headers={"Content-Type": "application/json"},
                json={
                    "text": text_content,
                    "model": "en"
                }
            )
            response.raise_for_status()
            logger.debug(f"Resposta SpaCy: {response.status_code}")
            
            entities = response.json()
            
            # Organiza as entidades por tipo
            processed_result = {
                "entities": entities,
                "entities_by_type": {},
                "total_entities": len(entities)
            }

            # Agrupa entidades por tipo
            for entity in entities:
                entity_type = entity["type"]
                if entity_type not in processed_result["entities_by_type"]:
                    processed_result["entities_by_type"][entity_type] = []
                
                processed_result["entities_by_type"][entity_type].append({
                    "text": entity["text"],
                    "start": entity["start"],
                    "end": entity["end"]
                })

            # Adiciona estatísticas
            processed_result["statistics"] = {
                "total": len(entities),
                "by_type": {
                    ent_type: len(entities_list)
                    for ent_type, entities_list in processed_result["entities_by_type"].items()
                }
            }

            return processed_result

    except Exception as e:
        logger.error(f"Erro detalhado SpaCy: {str(e)}")
        logger.error(f"Resposta: {getattr(e, 'response', {}).text if hasattr(e, 'response') else 'Sem resposta'}")
        raise Exception(f"Erro no processamento SpaCy: {str(e)}")

async def test_spacy():
    """Testa conexão com SpaCy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Testa especificamente o endpoint de entidades
            response = await client.post(
                f"{SPACY_URL}/ent",
                headers={"Content-Type": "application/json"},
                json={"text": "Test", "model": "en"}
            )
            logger.info(f"SpaCy NER test response: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"SpaCy test error: {str(e)}")
        return False

async def test_tika():
    """Testa conexão com Tika"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(TIKA_URL)
            logger.info(f"Tika status response: {response.status_code}")
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Tika test error: {str(e)}")
        return False

async def test_ocr():
    """Testa disponibilidade do OCR"""
    try:
        # Verifica se o tesseract está instalado
        version = pytesseract.get_tesseract_version()
        # Verifica se poppler-utils está instalado (necessário para pdf2image)
        subprocess.run(['pdftoppm', '-v'], capture_output=True, check=True)
        logger.info(f"OCR available - Tesseract version: {version}")
        return True
    except Exception as e:
        logger.error(f"OCR test error: {str(e)}")
        return False

@app.get("/check-services")
async def check_services():
    """Verifica disponibilidade de todos os serviços"""
    try:
        # Testa todos os serviços
        tika_available = await test_tika()
        spacy_available = await test_spacy()
        ocr_available = await test_ocr()
        
        services = [
            {"id": "tika", "isAvailable": tika_available},
            {"id": "spacy", "isAvailable": spacy_available},
            {"id": "ocrmypdf", "isAvailable": ocr_available}
        ]
        
        logger.info("Serviços verificados: %s", services)
        return {"services": services}
    except Exception as e:
        logger.error(f"Erro ao verificar serviços: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro ao verificar disponibilidade dos serviços"
        )

# Nova rota para download de arquivos
@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download de arquivo processado"""
    try:
        # Verifica primeiro no diretório de resultados
        file_path = RESULTS_DIR / filename
        if not file_path.exists():
            # Se não encontrar, verifica no diretório de uploads
            file_path = UPLOAD_DIR / filename
            if not file_path.exists():
                raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type='application/octet-stream'
        )
    except Exception as e:
        logger.error(f"Erro ao baixar arquivo: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

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

        # Adicionar informações de arquivo nos resultados
        results['file_info'] = {
            'original_name': file.filename,
            'safe_name': safe_filename,
            'download_url': f"/download/{safe_filename}"
        }

        # Processar com Tika
        if 'tika' in services_list:
            try:
                logger.debug("Iniciando processamento Tika")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.put(
                        f"{TIKA_URL}/tika",
                        content=content,
                        headers={
                            "Accept": "text/plain; charset=utf-8",
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
                spacy_result = await process_with_spacy(content, file.filename)
                results['spacy'] = spacy_result
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
                text_output_filename = f"{safe_filename}_texto.txt"
                text_output_path = RESULTS_DIR / text_output_filename
                
                with open(text_output_path, 'w', encoding='utf-8') as f:
                    f.write(extracted_text)
                
                results['ocrmypdf'] = {
                    'status': 'success',
                    'text_content': extracted_text,
                    'text_file': str(text_output_path),
                    'download_url': f"/download/{text_output_filename}"
                }
                logger.info("Processamento OCR e extração de texto concluídos")
                    
            except Exception as e:
                logger.error(f"Erro OCR: {str(e)}")
                results['ocrmypdf'] = {"error": str(e)}

        return {
            "status": "success",
            "message": "Processamento concluído com sucesso",
            "results": results,
            "services_used": services_list,
            "file_info": {
                'original_name': file.filename,
                'safe_name': safe_filename,
                'download_url': f"/download/{safe_filename}"
            }
        }

    except Exception as e:
        logger.error(f"Erro geral: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))