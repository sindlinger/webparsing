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
