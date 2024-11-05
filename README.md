# Sistema de Processamento de Documentos

Sistema para processamento de documentos com múltiplos serviços de análise e extração de informações.
(sindlinger@github.com)

## Serviços Disponíveis

- **Apache Tika**: Extração de texto e metadados de diversos formatos de documentos
- **SpaCy API**: Processamento de linguagem natural e análise de texto
- **OCRmyPDF**: OCR e otimização de PDFs
- **Backend FastAPI**: API REST para gerenciamento de documentos
- **Frontend Next.js**: Interface de usuário para upload e visualização

## Estrutura de Diretórios

- `backend/`
  - `main.py` - API FastAPI
  - `requirements.txt` - Dependências Python
  - `document_processor/` - Diretórios de trabalho
    - `uploads/` - Arquivos recebidos
    - `results/` - Resultados processados
    - `logs/` - Registros do sistema
- `frontend/`
  - `pages/` - Páginas Next.js
  - `components/` - Componentes React
  - `public/` - Arquivos estáticos

## Configuração do Ambiente

### Pré-requisitos
- Docker e Docker Compose
- Python 3.9+
- Node.js 16+
- npm/yarn

### Variáveis de Ambiente
O arquivo `.env` é criado automaticamente com as portas configuradas:
```
FRONTEND_PORT=3000
BACKEND_PORT=8000
TIKA_PORT=9998
SPACY_PORT=8080
OCRMYPDF_PORT=5000
```

## Instalação

1. **Configuração inicial**
```bash
# Criar e ativar ambiente virtual Python
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Instalar dependências do backend
cd backend
pip install -r requirements.txt
```

2. **Iniciar serviços Docker** *(no diretório raiz)*
```bash
docker-compose up -d
```

3. **Iniciar backend** 
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Configurar e iniciar frontend**
```bash
python setup_frontend.py
#npm install lucide-react @radix-ui/react-alert-dialog
cd frontend
npm run dev

```

## Uso

### Endpoints da API

- `GET /`: Verifica status da API
- `GET /status`: Status detalhado do sistema
- `POST /upload/`: Upload de documentos
- `GET /files/`: Lista arquivos processados

### Interface Web

Acesse `http://localhost:3000` para:
- Upload de documentos
- Seleção de serviços de processamento
- Visualização de resultados
- Monitoramento de status

## Comandos Úteis

### Docker
```bash
# Ver logs dos containers
docker-compose logs

# Reiniciar um serviço específico
docker-compose restart [serviço]

# Parar todos os serviços
docker-compose down
```

### Desenvolvimento
```bash
# Verificar API docs
http://localhost:8000/docs

# Logs do backend
tail -f backend/document_processor/logs/*

# Atualizar dependências
pip freeze > backend/requirements.txt
```

## Solução de Problemas

### Portas em Uso
O sistema verifica automaticamente portas em uso e seleciona alternativas disponíveis. As portas configuradas podem ser verificadas no arquivo `.env`.

### Serviços Docker
```bash
# Verificar status dos containers
docker ps

# Reiniciar container específico
docker restart [container_name]
```

### Logs e Debugging
- Logs do backend: `backend/document_processor/logs/`
- Logs Docker: `docker-compose logs -f`
- API Docs: `http://localhost:8000/docs`

## Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.