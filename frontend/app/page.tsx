"use client"

import React, { useState } from "react"
import { Upload, File, Clock } from "lucide-react"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"
import { Alert, AlertDescription } from "@/components/ui/alert"

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

    try {
      const formData = new FormData()
      formData.append("file", selectedFile)
      formData.append("services", JSON.stringify(selectedServices))

      const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      })
      
      if (!response.ok) {
        throw new Error("Erro ao processar o documento")
      }

      const data = await response.json()
      setResult({
        status: data.status,
        message: data.message,
        services: selectedServices,
      })
    } catch (error) {
      setResult({
        status: "error",
        message: (error as any).message || "Erro ao processar documento",
        services: [],
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
            <label className="block mb-2 font-medium">Serviços Disponíveis</label>
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