import os
import shutil
from pathlib import Path
import subprocess
import socket
import time

def is_port_in_use(port):
    """Verifica se uma porta está em uso"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return False
        except socket.error:
            return True

def find_available_port(start_port):
    """Encontra próxima porta disponível a partir de start_port"""
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def get_service_ports():
    """Define e verifica portas para cada serviço"""
    default_ports = {
        'frontend': 3000,
        'backend': 8000,
        'tika': 9998,
        'spacy': 8080,
        'ocrmypdf': 5000
    }
    
    actual_ports = {}
    print("\n🔍 Verificando portas disponíveis...")
    
    for service, default_port in default_ports.items():
        if is_port_in_use(default_port):
            new_port = find_available_port(default_port)
            print(f"→ {service}: porta {default_port} ocupada, usando {new_port}")
            actual_ports[service] = new_port
        else:
            print(f"→ {service}: usando porta padrão {default_port}")
            actual_ports[service] = default_port
    
    return actual_ports

def run_command(command):
    """Executa um comando shell e retorna o resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        print(f"Erro ao executar comando {command}: {e}")
        return None

def cleanup_docker_resources():
    """Limpa recursos Docker existentes"""
    print("\n🧹 Limpando recursos Docker existentes...")
    
    # Lista containers usando a rede
    containers = run_command("docker ps -a --filter network=doc_processing_network -q")
    if containers:
        print("→ Parando e removendo containers conectados à rede...")
        run_command("docker stop $(docker ps -a --filter network=doc_processing_network -q)")
        run_command("docker rm $(docker ps -a --filter network=doc_processing_network -q)")
    
    # Remove a rede se existir
    network_exists = run_command("docker network ls --filter name=doc_processing_network -q")
    if network_exists:
        print("→ Removendo rede doc_processing_network...")
        run_command("docker network rm doc_processing_network")
    
    print("✅ Limpeza Docker concluída!")

def create_project_structure():
    """Cria a estrutura completa do projeto"""
    
    # Limpar recursos Docker primeiro
    cleanup_docker_resources()
    
    # Obter portas disponíveis
    ports = get_service_ports()
    
    print("\n🚀 Criando nova estrutura do projeto...")
    
    # Definir diretório raiz do projeto
    root_dir = Path.cwd()
    
    # Criar estrutura de diretórios
    directories = {
        'backend': [
            'document_processor/uploads',
            'document_processor/results',
            'document_processor/logs',
        ],
        'frontend': [
            'pages',
            'components',
            'public',
        ]
    }
    
    # Criar diretórios
    for main_dir, subdirs in directories.items():
        main_path = root_dir / main_dir
        main_path.mkdir(exist_ok=True)
        for subdir in subdirs:
            (main_path / subdir).mkdir(parents=True, exist_ok=True)
    
    # Criar main.py com a porta correta
    main_py_content = f'''from fastapi import FastAPI, HTTPException, UploadFile, File
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
    allow_origins=[f"http://localhost:{ports['frontend']}"],
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
    return {{"message": "Document Processing API is running"}}

@app.get("/status")
async def status():
    return {{
        "status": "online",
        "directories": {{
            "uploads": UPLOAD_DIR.exists(),
            "results": RESULTS_DIR.exists(),
            "logs": LOGS_DIR.exists()
        }}
    }}

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {{
            "filename": file.filename,
            "status": "success",
            "message": "File uploaded successfully"
        }}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/")
async def list_files():
    uploads = [f.name for f in UPLOAD_DIR.glob("*") if f.is_file()]
    results = [f.name for f in RESULTS_DIR.glob("*") if f.is_file()]
    
    return {{
        "uploads": uploads,
        "results": results
    }}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port={ports['backend']}, reload=True)
'''
    
    # Criar requirements.txt
    requirements_txt_content = '''fastapi==0.68.1
uvicorn==0.15.0
python-multipart==0.0.5
httpx==0.19.0
aiofiles==0.7.0
pytesseract==0.3.8
Pillow==8.3.2
spacy==3.1.3
PyPDF2==1.26.0
python-jose==3.3.0
passlib==1.7.4
python-dotenv==0.19.0'''

    # Criar docker-compose.yml com as portas corretas
    docker_compose_content = f'''version: '3.8'

services:
  tika:
    image: apache/tika:latest-full
    container_name: tika
    ports:
      - "{ports['tika']}:9998"
    networks:
      - doc_processing_network
    restart: unless-stopped

  spacy:
    image: jgontrum/spacyapi:latest
    container_name: spacy
    ports:
      - "{ports['spacy']}:80"
    networks:
      - doc_processing_network
    restart: unless-stopped

  ocrmypdf:
    image: jbarlow83/ocrmypdf
    container_name: ocrmypdf
    ports:
      - "{ports['ocrmypdf']}:5000"
    networks:
      - doc_processing_network
    restart: unless-stopped

networks:
  doc_processing_network:
    name: doc_processing_network
    driver: bridge'''

    # Criar .env com as portas
    env_content = f'''FRONTEND_PORT={ports['frontend']}
BACKEND_PORT={ports['backend']}
TIKA_PORT={ports['tika']}
SPACY_PORT={ports['spacy']}
OCRMYPDF_PORT={ports['ocrmypdf']}
'''

    # Salvar arquivos
    files_to_create = {
        'backend/main.py': main_py_content,
        'backend/requirements.txt': requirements_txt_content,
        'docker-compose.yml': docker_compose_content,
        '.env': env_content
    }

    for file_path, content in files_to_create.items():
        full_path = root_dir / file_path
        full_path.parent.mkdir(exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)

    print("\n✅ Estrutura do projeto criada com sucesso!")
    print("\n📌 Portas configuradas:")
    for service, port in ports.items():
        print(f"→ {service}: {port}")
    
    print("\n📝 Próximos passos:")
    print("1. Execute: docker-compose up -d")
    print("2. Entre no diretório backend: cd backend")
    print("3. Instale as dependências: pip install -r requirements.txt")
    print(f"4. Inicie o backend: uvicorn main:app --reload --host 0.0.0.0 --port {ports['backend']}")
    print("5. Em outro terminal, configure o frontend:")
    print("   cd frontend")
    print("   npx create-next-app@latest . --use-npm --typescript --tailwind --eslint")
    print("   npm install lucide-react @radix-ui/react-alert-dialog")
    print(f"   npm run dev -- -p {ports['frontend']}")

if __name__ == "__main__":
    try:
        create_project_structure()
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        print("Por favor, verifique as permissões e tente novamente.")