# Guia de Instalação - Sistema de Processamento de Documentos

## Pré-requisitos do Sistema

### Requisitos de Hardware Recomendados
- CPU: 4+ cores
- RAM: 16GB+ (8GB mínimo)
- Espaço em Disco: 20GB+ livre

### Software Base
```bash
# Ubuntu/Debian
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y \
    python3.9 \
    python3-pip \
    python3-venv \
    docker.io \
    docker-compose \
    git \
    build-essential \
    tesseract-ocr

# MacOS (usando Homebrew)
brew update
brew install \
    python@3.9 \
    docker \
    docker-compose \
    git \
    tesseract
```

## 1. Configuração do Ambiente Python

### Criar e ativar ambiente virtual
```bash
# Criar diretório do projeto
mkdir document_processor
cd document_processor

# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
# Linux/MacOS:
source venv/bin/activate
# Windows:
.\venv\Scripts\activate
```

### Instalar dependências Python
Criar arquivo `requirements.txt`:
```text
fastapi==0.68.1
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
python-dotenv==0.19.0
aiohttp==3.8.1
pydantic==1.8.2
```

Instalar dependências:
```bash
pip install -r requirements.txt

# Baixar modelo SpaCy
python -m spacy download en_core_web_sm
```

## 2. Configuração do Docker

### Iniciar serviço Docker
```bash
# Linux
sudo systemctl start docker
sudo systemctl enable docker

# Adicionar usuário ao grupo docker (Linux)
sudo usermod -aG docker $USER
# Fazer logout e login para aplicar as mudanças
```

### Criar rede Docker
```bash
docker network create doc_processing_network
```

### Configurar e iniciar serviços
j
#### Apache Tika
```bash
docker pull apache/tika:latest-full
docker run -d \
    --name tika \
    --network doc_processing_network \
    -p 9998:9998 \
    apache/tika:latest-full
```

#### SpaCy API
```bash
docker pull jgontrum/spacyapi:latest
docker run -d \
    --name spacy \
    --network doc_processing_network \
    -p 8080:80 \
    jgontrum/spacyapi:latest
```

#### OCRmyPDF
```bash
docker pull jbarlow83/ocrmypdf
docker run -d \
    --name ocrmypdf \
    --network doc_processing_network \
    -p 5000:5000 \
    jbarlow83/ocrmypdf
```

## 3. Configuração do Ollama
```bash
# Linux
curl https://ollama.ai/install.sh | sh

# MacOS
brew install ollama

# Iniciar Ollama
ollama serve

# Em outro terminal, baixar o modelo (exemplo com Llama 2)
ollama pull llama2
```

## 4. Estrutura de Diretórios

Criar a seguinte estrutura:
```bash
mkdir -p document_processor/{uploads,results,logs}
```

## 5. Variáveis de Ambiente

Criar arquivo `.env`:
```bash
cat << EOF > .env
UPLOAD_DIR=uploads
RESULTS_DIR=results
OLLAMA_URL=http://localhost:11434
TIKA_URL=http://localhost:9998
SPACY_URL=http://localhost:8080
LOG_LEVEL=INFO
EOF
```

## 6. Verificação da Instalação

Script de verificação `check_installation.py`:
```python
import httpx
import asyncio
import os
from pathlib import Path

async def check_services():
    services = {
        'Ollama': 'http://localhost:11434/api/tags',
        'Tika': 'http://localhost:9998/tika',
        'SpaCy': 'http://localhost:8080/status',
    }
    
    async with httpx.AsyncClient() as client:
        for service, url in services.items():
            try:
                response = await client.get(url)
                print(f"✅ {service}: OK")
            except Exception as e:
                print(f"❌ {service}: Failed - {str(e)}")

    # Verificar diretórios
    dirs = ['uploads', 'results', 'logs']
    for dir_name in dirs:
        path = Path(dir_name)
        if path.exists() and path.is_dir():
            print(f"✅ Directory {dir_name}: OK")
        else:
            print(f"❌ Directory {dir_name}: Not found")

if __name__ == "__main__":
    asyncio.run(check_services())
```

Execute o script:
```bash
python check_installation.py
```

## 7. Iniciar o Backend

```bash
# Modo desenvolvimento
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Modo produção
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 8. Endpoints Disponíveis

Após iniciar o servidor, acesse:
- Documentação Swagger: http://localhost:8000/docs
- Documentação ReDoc: http://localhost:8000/redoc

## Solução de Problemas Comuns

### Permissões Docker
```bash
# Se houver problemas de permissão com Docker
sudo chmod 666 /var/run/docker.sock
```

### Problemas com Tesseract
```bash
# Verificar instalação Tesseract
tesseract --version

# Se necessário, instalar dados adicionais
sudo apt-get install tesseract-ocr-por  # Para português
```

### Problemas com SpaCy
```bash
# Reinstalar SpaCy e modelos
pip uninstall spacy
pip install -U spacy
python -m spacy download en_core_web_sm
```

### Logs
```bash
# Verificar logs dos containers
docker logs tika
docker logs spacy
docker logs ocrmypdf

# Verificar logs do Ollama
journalctl -u ollama
```

## Monitoramento

Para monitorar o uso de recursos:
```bash
# Uso dos containers
docker stats

# Uso geral do sistema
htop
```

## Backup

Script para backup `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="backups/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup dos dados
tar -czf $BACKUP_DIR/data.tar.gz uploads results

# Backup das configurações
cp .env $BACKUP_DIR/
cp requirements.txt $BACKUP_DIR/
```

Tornar executável:
```bash
chmod +x backup.sh
```