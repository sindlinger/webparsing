"use client"

import React, { useState } from "react"
import { Upload, Clock, BookOpen, X, Download } from "lucide-react"
import Link from "next/link"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Button } from "@/components/ui/button"

const DocumentProcessor = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [selectedServices, setSelectedServices] = useState<string[]>([])
  const [processing, setProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [results, setResults] = useState<{[key: string]: any}>({})

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
    const files = Array.from(event.target.files || [])
    setSelectedFiles(prev => [...prev, ...files])
    setResults({})
    setError(null)
    
    const hasPDF = files.some(file => file.type === 'application/pdf')
    if (hasPDF) {
      setSelectedServices(prev => prev.includes('ocrmypdf') ? prev : [...prev, 'ocrmypdf'])
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
    setResults({})
  }

  const toggleService = (serviceId: string) => {
    setSelectedServices((prev) =>
      prev.includes(serviceId)
        ? prev.filter((id) => id !== serviceId)
        : [...prev, serviceId]
    )
  }

  const handleDownload = async (url: string, filename: string) => {
    try {
      const response = await fetch(`http://localhost:8000${url}`)
      if (!response.ok) throw new Error('Erro ao baixar arquivo')
      
      const blob = await response.blob()
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.setAttribute('download', filename)
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      console.error('Download error:', error)
      setError('Erro ao baixar arquivo')
    }
  }

  const handleSubmit = async () => {
    if (selectedFiles.length === 0 || selectedServices.length === 0) return
  
    setProcessing(true)
    setResults({})
    setError(null)
  
    try {
      const processResults: { [key: string]: any } = {}
      
      // Process each file sequentially
      for (const file of selectedFiles) {
        const formData = new FormData()
        formData.append("file", file)
        formData.append("services", JSON.stringify(selectedServices))
    
        const response = await fetch("http://localhost:8000/upload", {
          method: "POST",
          body: formData,
        })
    
        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(`Erro ao processar ${file.name}: ${errorData.detail}`)
        }
    
        const data = await response.json()
        processResults[file.name] = data
      }
      
      setResults(processResults)
    } catch (error) {
      console.error('Processing error:', error)
      setError((error as Error).message || "Erro ao processar documentos")
      setResults({})
    } finally {
      setProcessing(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">Processador de Documentos</h1>
        <Link href="/docs/spacy" target="_blank">
          <Button 
            variant="outline"
            className="flex items-center gap-2"
          >
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
            <label className="block mb-2 font-medium">Upload de Arquivos</label>
            <div className="flex items-center justify-center w-full">
              <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                <div className="flex flex-col items-center justify-center pt-5 pb-6">
                  <Upload className="w-8 h-8 mb-2 text-gray-500" />
                  <p className="mb-2 text-sm text-gray-500">
                    Clique ou arraste arquivos
                  </p>
                </div>
                <input
                  type="file"
                  className="hidden"
                  onChange={handleFileChange}
                  accept=".pdf,.png,.jpg,.jpeg,.doc,.docx,.txt"
                  multiple
                />
              </label>
            </div>
            
            {/* Selected Files List */}
            {selectedFiles.length > 0 && (
              <div className="mt-4">
                <h4 className="font-medium mb-2">Arquivos Selecionados:</h4>
                <div className="space-y-2">
                  {selectedFiles.map((file, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm">{file.name}</span>
                      <button
                        onClick={() => removeFile(index)}
                        className="p-1 hover:bg-gray-200 rounded"
                      >
                        <X className="h-4 w-4 text-gray-500" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
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
              selectedFiles.length > 0 && selectedServices.length > 0 && !processing
                ? "bg-blue-500 hover:bg-blue-600 text-white"
                : "bg-gray-200 text-gray-500 cursor-not-allowed"
            }`}
            onClick={handleSubmit}
            disabled={selectedFiles.length === 0 || selectedServices.length === 0 || processing}
          >
            {processing ? (
              <span className="flex items-center justify-center">
                <Clock className="animate-spin -ml-1 mr-2 h-5 w-5" />
                Processando...
              </span>
            ) : (
              `Processar ${selectedFiles.length} Documento${selectedFiles.length !== 1 ? 's' : ''}`
            )}
          </button>
        </CardContent>
      </Card>

      {/* Results Section */}
      {Object.keys(results).length > 0 && (
        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Resultados do Processamento</CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue={Object.keys(results)[0]} className="w-full">
              <TabsList className="w-full flex-wrap">
                {Object.keys(results).map(filename => (
                  <TabsTrigger key={filename} value={filename}>
                    {filename}
                  </TabsTrigger>
                ))}
              </TabsList>

              {Object.entries(results).map(([filename, result]) => (
                <TabsContent key={filename} value={filename}>
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

                            {/* Botão de download do arquivo original */}
                            {result.file_info && (
                              <Button
                                variant="outline"
                                className="mt-4 flex items-center gap-2"
                                onClick={() => handleDownload(
                                  result.file_info.download_url,
                                  result.file_info.original_name
                                )}
                              >
                                <Download className="h-4 w-4" />
                                Baixar Arquivo Original
                              </Button>
                            )}
                          </div>
                        </AlertDescription>
                      </Alert>
                    </TabsContent>

                    {result.results.ocrmypdf && (
                      <TabsContent value="ocr">
                        <div className="bg-gray-50 rounded-lg p-4">
                          <div className="flex justify-between items-center mb-4">
                            <h4 className="font-medium">Texto Extraído do PDF:</h4>
                            {/* Botão de download do texto extraído */}
                            <Button
                              variant="outline"
                              className="flex items-center gap-2"
                              onClick={() => handleDownload(
                                result.results.ocrmypdf.download_url,
                                `${result.file_info.original_name}_texto.txt`
                              )}
                            >
                              <Download className="h-4 w-4" />
                              Baixar Texto
                            </Button>
                          </div>
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
                </TabsContent>
              ))}
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default DocumentProcessor