import os
import shutil
from pathlib import Path
import subprocess
import sys
import json

def run_command(command, cwd=None):
    """Executa um comando shell e retorna o resultado"""
    try:
        process = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            text=True,
            capture_output=False  # Permite ver a saída em tempo real
        )
        return process.returncode == 0
    except Exception as e:
        print(f"Erro ao executar comando {command}: {e}")
        return False

def create_frontend_structure():
    """Cria a estrutura do frontend"""
    
    print("\n🚀 Configurando o frontend...")
    
    # Definir diretório raiz do frontend
    root_dir = Path.cwd() / 'frontend'
    
    # Remover diretório frontend se existir
    if root_dir.exists():
        print("→ Removendo diretório frontend existente...")
        try:
            shutil.rmtree(root_dir)
            print("✅ Diretório frontend removido com sucesso")
        except Exception as e:
            print(f"❌ Erro ao remover diretório: {e}")
            return False
    
    # Criar novo diretório frontend
    print("→ Criando novo diretório frontend...")
    root_dir.mkdir(exist_ok=True)

    print("\n📦 Instalando Next.js...")
    
    # Se estiver no diretório errado, entre no diretório frontend
    if str(Path.cwd()).endswith('webparsing'):
        print("→ Entrando no diretório frontend...")
        os.chdir(root_dir)
    
    print("→ Diretório atual:", os.getcwd())
    
    # Criar projeto Next.js
    create_next_app_command = 'npx create-next-app@latest . --ts --tailwind --eslint --app --use-npm --no-git'
    result = subprocess.run(
        create_next_app_command,
        shell=True,
        cwd=str(root_dir),
        text=True,
        capture_output=False
    )
    
    if result.returncode != 0:
        print("❌ Erro ao criar projeto Next.js")
        return False

    print("\n📦 Instalando dependências adicionais...")
    if not run_command('npm install lucide-react @radix-ui/react-alert-dialog', cwd=str(root_dir)):
        print("❌ Erro ao instalar dependências adicionais")
        return False

    # Conteúdo dos componentes
    card_content = '''import * as React from "react"

export interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`rounded-lg border bg-card text-card-foreground shadow-sm ${className}`}
        {...props}
      />
    )
  }
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`flex flex-col space-y-1.5 p-6 ${className}`}
        {...props}
      />
    )
  }
)
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLHeadingElement>>(
  ({ className, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={`text-2xl font-semibold leading-none tracking-tight ${className}`}
        {...props}
      />
    )
  }
)
CardTitle.displayName = "CardTitle"

const CardContent = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`p-6 pt-0 ${className}`}
        {...props}
      />
    )
  }
)
CardContent.displayName = "CardContent"

export { Card, CardHeader, CardTitle, CardContent }
'''

    alert_content = '''import * as React from "react"

export interface AlertProps extends React.HTMLAttributes<HTMLDivElement> {}

const Alert = React.forwardRef<HTMLDivElement, AlertProps>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        role="alert"
        className={`relative w-full rounded-lg border p-4 [&>svg]:absolute [&>svg]:text-foreground [&>svg]:left-4 [&>svg]:top-4 [&>svg+div]:translate-y-[-3px] [&:has(svg)]:pl-11 ${className}`}
        {...props}
      />
    )
  }
)
Alert.displayName = "Alert"

const AlertDescription = React.forwardRef<HTMLParagraphElement, React.HTMLAttributes<HTMLParagraphElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={`text-sm [&_p]:leading-relaxed ${className}`}
        {...props}
      />
    )
  }
)
AlertDescription.displayName = "AlertDescription"

export { Alert, AlertDescription }
'''

    page_content = '''\'use client\'

import React, { useState } from \'react\'
import { Upload, File, Clock } from \'lucide-react\'
import { Card, CardHeader, CardTitle, CardContent } from \'@/components/ui/card\'
import { Alert, AlertDescription } from \'@/components/ui/alert\'

const DocumentProcessor = () => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [processing, setProcessing] = useState(false)
  const [result, setResult] = useState<{
    status: string
    message: string
    services: string[]
  } | null>(null)

  const services = [
    {
      id: \'tika\',
      name: \'Apache Tika\',
      description: \'Extração de texto e metadados\',
      capabilities: [\'OCR\', \'Extração de texto\', \'Metadados\']
    },
    {
      id: \'spacy\',
      name: \'SpaCy\',
      description: \'Processamento de linguagem natural\',
      capabilities: [\'NER\', \'Análise sintática\', \'Classificação\']
    },
    {
      id: \'ocrmypdf\',
      name: \'OCRmyPDF\',
      description: \'OCR especializado\',
      capabilities: [\'OCR\', \'Conversão PDF\', \'Otimização\']
    }
  ]

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setResult(null)
    }
  }

  const toggleService = (serviceId: string) => {
    setSelectedServices(prev => 
      prev.includes(serviceId)
        ? prev.filter(id => id !== serviceId)
        : [...prev, serviceId]
    )
  }

  const handleSubmit = async () => {
    if (!selectedFile || selectedServices.length === 0) return
    
    setProcessing(true)
    setResult(null)
    
    try {
      const formData = new FormData()
      formData.append(\'file\', selectedFile)
      formData.append(\'services\', JSON.stringify(selectedServices))

      const response = await fetch(\'http://localhost:8000/upload\', {
        method: \'POST\',
        body: formData,
      })

      const data = await response.json()
      setResult({
        status: \'success\',
        message: \'Documento processado com sucesso!\',
        services: selectedServices
      })
    } catch (error) {
      setResult({
        status: \'error\',
        message: \'Erro ao processar documento\',
        services: []
      })
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <Card>
        <CardHeader>
          <CardTitle>Processador de Documentos</CardTitle>
        </CardHeader>
        <CardContent>
          {/* Upload Section */}
          <div className="mb-6">
            <label className="block mb-2 font-medium">Upload de Arquivo</label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-8 h-8 mb-2 text-gray-500" />
                  <p className="mb-2 text-sm text-gray-500">
                    {selectedFile ? selectedFile.name : \'Clique ou arraste um arquivo\'}
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
            <label className="block mb-2 font-medium">Serviços Disponíveis</label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {services.map((service) => (
                <div
                  key={service.id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedServices.includes(service.id)
                      ? \'border-blue-500 bg-blue-50\'
                      : \'border-gray-200 hover:border-blue-300\'
                  }`}
                  onClick={() => toggleService(service.id)}
                >
                  <div className="font-medium mb-1">{service.name}</div>
                  <div className="text-sm text-gray-600 mb-2">{service.description}</div>
                  <div className="flex flex-wrap gap-2">
                    {service.capabilities.map((cap) => (
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
                ? \'bg-blue-500 hover:bg-blue-600 text-white\'
                : \'bg-gray-200 text-gray-500 cursor-not-allowed\'
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
              \'Processar Documento\'
            )}
          </button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {result && (
        <Alert className="mt-4">
          <AlertDescription>
            <div className="text-sm">
              <p className="font-medium mb-2">{result.message}</p>
              <p>Serviços utilizados:</p>
              <ul className="list-disc ml-5">
                {result.services.map(serviceId => (
                  <li key={serviceId}>
                    {services.find(s => s.id === serviceId)?.name}
                  </li>
                ))}
              </ul>
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  )
}

export default DocumentProcessor
'''

    # Criar arquivos dos componentes
    print("\n📦 Criando componentes...")
    files_to_create = {
        'components/ui/card.tsx': card_content,
        'components/ui/alert.tsx': alert_content,
        'app/page.tsx': page_content
    }

    for file_path, content in files_to_create.items():
        full_path = root_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w') as f:
            f.write(content)
    
    print("\n✅ Frontend configurado com sucesso!")
    print("\n📝 Próximos passos:")
    print("1. Entre no diretório frontend: cd frontend")
    print("2. Inicie o servidor de desenvolvimento: npm run dev")
    print("3. Acesse http://localhost:3000 no navegador")

if __name__ == "__main__":
    try:
        create_frontend_structure()
    except Exception as e:
        print(f"\n❌ Erro durante a execução: {e}")
        print("Por favor, verifique as permissões e tente novamente.")