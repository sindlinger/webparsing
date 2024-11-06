#!/bin/bash

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Criando estrutura de documentação do SpaCy...${NC}"

# Criar diretório docs dentro de app se não existir
mkdir -p app/docs/spacy
# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Instalando e configurando componentes shadcn/ui...${NC}"

# Instalar dependências do shadcn/ui
echo -e "${GREEN}Instalando dependências...${NC}"
npx shadcn-ui@latest init

# Instalar componentes necessários
echo -e "${GREEN}Instalando componentes...${NC}"
npx shadcn-ui@latest add button
npx shadcn-ui@latest add card
npx shadcn-ui@latest add alert
npx shadcn-ui@latest add tabs

echo -e "${GREEN}Configuração concluída!${NC}"
echo "Componentes instalados:"echo "- Button"
echo "- Card"
echo "- Alert"
echo "- Tabs"
# Criar página da documentação
echo -e "${GREEN}Criando página de redirecionamento da documentação...${NC}"
cat > app/docs/spacy/page.tsx << 'EOF'
"use client"
 
import { useEffect } from "react"
 
export default function SpacyDocsPage() {
  useEffect(() => {
    window.location.href = '/spacy-docs.html'
  }, [])
 
  return (
    <div className="flex justify-center items-center h-screen">
      Carregando documentação...
    </div>
  )
}
EOF

# Criar arquivo de documentação HTML
echo -e "${GREEN}Criando arquivo de documentação HTML...${NC}"
cat > public/spacy-docs.html << 'EOF'
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>SpaCy API Documentation</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      line-height: 1.6;
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }
    .endpoint {
      border: 1px solid #ddd;
      border-radius: 4px;
      padding: 20px;
      margin-bottom: 20px;
    }
    .example {
      background-color: #f5f5f5;
      padding: 15px;
      border-radius: 4px;
      overflow-x: auto;
    }
    .entity-type {
      display: inline-block;
      padding: 2px 8px;
      border-radius: 3px;
      margin: 2px;
      font-size: 0.9em;
    }
    .entity-person { background-color: #ffd700; }
    .entity-org { background-color: #98fb98; }
    .entity-gpe { background-color: #87ceeb; }
  </style>
</head>
<body>
  <h1>Documentação SpaCy API</h1>
  
  <div class="endpoint">
    <h2>Endpoint: /ent (Extração de Entidades)</h2>
    <p>Extrai entidades nomeadas do texto como pessoas, organizações, locais, etc.</p>
    
    <h3>Requisição:</h3>
    <pre class="example">
curl -X POST http://localhost:8080/ent \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Microsoft was founded by Bill Gates in Seattle",
    "model": "en"
  }'</pre>
    
    <h3>Resposta:</h3>
    <pre class="example">[
  {
    "text": "Microsoft",
    "type": "ORG",
    "start": 0,
    "end": 9
  },
  {
    "text": "Bill Gates",
    "type": "PERSON",
    "start": 25,
    "end": 35
  },
  {
    "text": "Seattle",
    "type": "GPE",
    "start": 39,
    "end": 46
  }
]</pre>

    <h3>Tipos de Entidades:</h3>
    <div>
      <span class="entity-type entity-person">PERSON</span> - Pessoas
      <span class="entity-type entity-org">ORG</span> - Organizações
      <span class="entity-type entity-gpe">GPE</span> - Locais Geopolíticos
    </div>
  </div>

  <div class="endpoint">
    <h2>Endpoint: /dep (Análise de Dependências)</h2>
    <p>Analisa a estrutura sintática e dependências entre palavras no texto.</p>
    
    <h3>Requisição:</h3>
    <pre class="example">
curl -X POST http://localhost:8080/dep \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test",
    "model": "en"
  }'</pre>
    
    <h3>Resposta:</h3>
    <pre class="example">{
  "words": [
    {
      "text": "This",
      "tag": "DT"
    },
    {
      "text": "is",
      "tag": "VBZ"
    },
    {
      "text": "a test",
      "tag": "NN"
    }
  ],
  "arcs": [
    {
      "start": 0,
      "end": 1,
      "label": "nsubj",
      "dir": "left",
      "text": "This"
    },
    {
      "start": 1,
      "end": 2,
      "label": "attr",
      "dir": "right",
      "text": "a test"
    }
  ]
}</pre>
  </div>

  <div class="endpoint">
    <h2>Endpoint: /models</h2>
    <p>Lista os modelos disponíveis.</p>
    
    <h3>Requisição:</h3>
    <pre class="example">curl http://localhost:8080/models</pre>
    
    <h3>Resposta:</h3>
    <pre class="example">["en"]</pre>
  </div>

  <div class="endpoint">
    <h2>Notas Importantes</h2>
    <ul>
      <li>O modelo disponível é apenas em inglês ("en")</li>
      <li>Todos os endpoints esperam o parâmetro "model":"en" no JSON</li>
      <li>O tamanho máximo do texto pode ser limitado pelo servidor</li>
      <li>As respostas incluem posições no texto (start/end) para mapeamento preciso</li>
    </ul>
  </div>
</body>
</html>
EOF

# Atualizar o page.tsx principal
echo -e "${GREEN}Atualizando página principal...${NC}"
cat > app/page.tsx << 'EOF'
"use client"

import React, { useState } from "react"
import { Upload, Clock, BookOpen } from "lucide-react"
import Link from "next/link"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"

const DocumentProcessor = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<any | null>(null)

  const services = [
    {
      id: "tika",
      name: "Apache Tika",
      description: "Extração de texto e metadados",
      capabilities: ["OCR", "Extração de texto", "Metadados"],
    },
    {
      id: "spacy",
      name: "SpaCy",
      description: "Processamento de linguagem natural",
      capabilities: ["NER", "Análise sintática", "Classificação"],
    },
    {
      id: "ocrmypdf",
      name: "OCRmyPDF",
      description: "OCR especializado",
      capabilities: ["OCR", "Conversão PDF", "Otimização"],
    },
  ]

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setResult(null)
      setError(null)
      
      if (file.type === 'application/pdf') {
        setSelectedServices(prev => prev.includes('ocrmypdf') ? prev : [...prev, 'ocrmypdf'])
      }
    }
  }

  const toggleService = (serviceId: string) => {
    setSelectedServices((prev) =>
      prev.includes(serviceId)
        ? prev.filter((id) => id !== serviceId)
        : [...prev, serviceId]
    )
  }

  const handleSubmit = async () => {
    if (!selectedFile || selectedServices.length === 0) return
  
    setProcessing(true)
    setResult(null)
    setError(null)
  
    try {
      const formData = new FormData()
      formData.append("file", selectedFile)
      formData.append("services", JSON.stringify(selectedServices))
  
      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })
  
      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Erro ao processar documento")
      }
  
      const data = await response.json()
      setResult(data)
    } catch (error) {
      console.error('Processing error:', error)
      setError((error as Error).message || "Erro ao processar documento")
      setResult(null)
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Processador de Documentos</h1>
        <Link href="/docs/spacy" target="_blank">
          <Button variant="outline" className="flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Documentação SpaCy
          </Button>
        </Link>
      </div>

      <Card>
        <CardContent className="pt-6">
          {error && (
            <Alert className="mb-4">
              <AlertDescription className="text-red-600">{error}</AlertDescription>
            </Alert>
          )}

          {/* Upload Section */}
          <div className="mb-6">
            <label className="block mb-2 font-medium">Upload de Arquivo</label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-8 h-8 mb-2 text-gray-500" />
                  <p className="mb-2 text-sm text-gray-500">
                    {selectedFile ? selectedFile.name : "Clique ou arraste um arquivo"}
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.txt"
                />
              </label>
            </div>
          </div>

          {/* Services Selection */}
          <div className="mb-6">
            <label className="block mb-2 font-medium">
              Serviços Selecionados: {selectedServices.join(', ')}
            </label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {services.map(service => (
                <div
                  key={service.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedServices.includes(service.id)
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-blue-300"
                  }`}
                  onClick={() => toggleService(service.id)}
                  role="button"
                  tabIndex={0}
                  onKeyPress={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      toggleService(service.id)
                    }
                  }}
                >
                  <div className="font-medium mb-1">{service.name}</div>
                  <div className="text-sm text-gray-600 mb-2">{service.description}</div>
                  <div className="flex flex-wrap gap-2">
                    {service.capabilities.map(cap => (
                      <span
                        key={cap}
                        className="px-2 py-1 text-xs bg-gray-100 rounded-full"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Submit Button */}
          <button
            className={`w-full py-2 px-4 rounded-lg font-medium transition-colors ${
              selectedFile && selectedServices.length > 0 && !processing
                ? "bg-blue-500 hover:bg-blue-600 text-white"
                : "bg-gray-200 text-gray-500 cursor-not-allowed"
            }`}
            onClick={handleSubmit}
            disabled={!selectedFile || selectedServices.length === 0 || processing}
          >
            {processing ? (
              <span className="flex items-center justify-center">
                <Clock className="animate-spin -ml-1 mr-2 h-5 w-5" />
                Processando...
              </span>
            ) : (
              "Processar Documento"
            )}
          </button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {result && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Resultados do Processamento</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="summary" className="w-full">
              <TabsList className="w-full">
                <TabsTrigger value="summary">Resumo</TabsTrigger>
                {result.results.ocrmypdf && (
                  <TabsTrigger value="ocr">Texto Extraído</TabsTrigger>
                )}
                {result.results.tika && (
                  <TabsTrigger value="tika">Tika</TabsTrigger>
                )}
                {result.results.spacy && (
                  <TabsTrigger value="spacy">SpaCy</TabsTrigger>
                )}
              </TabsList>

              <TabsContent value="summary">
                <Alert>
                  <AlertDescription>
                    <div className="text-sm">
                      <p className="font-medium mb-2">{result.message}</p>
                      <p>Serviços utilizados:</p>
                      <ul className="list-disc ml-5">
                        {result.services_used.map((serviceId: string) => (
                          <li key={serviceId}>
                            {services.find(s => s.id === serviceId)?.name}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </AlertDescription>
                </Alert>
              </TabsContent>

              {result.results.ocrmypdf && (
                <TabsContent value="ocr">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium mb-2">Texto Extraído do PDF:</h4>
                    <div className="whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded border max-h-96 overflow-y-auto">
                      {result.results.ocrmypdf.text_content || 'Nenhum texto extraído'}
                    </div>
                  </div>
                </TabsContent>
              )}

              {result.results.tika && (
                <TabsContent value="tika">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium mb-2">Resultado Tika:</h4>
                    <div className="whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded border max-h-96 overflow-y-auto">
                      {result.results.tika.text || JSON.stringify(result.results.tika, null, 2)}
                    </div>
                  </div>
                </TabsContent>
              )}

              {result.results.spacy && (
                <TabsContent value="spacy">
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h4 className="font-medium mb-2">Análise SpaCy:</h4>
                    <div className="whitespace-pre-wrap font-mono text-sm bg-white p-4 rounded border max-h-96 overflow-y-auto">
                      {JSON.stringify(result.results.spacy, null, 2)}
                    </div>
                  </div>
                </TabsContent>
              )}
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default DocumentProcessor
EOF

echo -e "${GREEN}Estrutura criada com sucesso!${NC}"
echo -e "${BLUE}Estrutura de arquivos:${NC}"
echo "frontend/"
echo "├── app/"
echo "│   ├── page.tsx (atualizado)"
echo "│   └── docs/"
echo "│       └── spacy/"
echo "│           └── page.tsx"
echo "└── public/"
echo "    └── spacy-docs.html"
echo ""
echo -e "${BLUE}Para usar:${NC}"
echo "1. Salve o script como setup-spacy-docs.sh"
echo "2. Execute: chmod +x setup-spacy-docs.sh"
echo "3. Execute: ./setup-spacy-docs.sh"