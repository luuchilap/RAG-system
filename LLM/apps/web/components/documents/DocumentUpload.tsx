"use client"

import { useState, useRef } from "react"
import { Button } from "@workspace/ui/components/button"
import { Progress } from "@workspace/ui/components/progress"
import { Alert, AlertDescription } from "@workspace/ui/components/alert"
import { Upload, File, X } from "lucide-react"
import { uploadDocument } from "@/lib/api"

interface DocumentUploadProps {
  onUploadComplete?: (response: { document_id: string; filename: string; chunk_count: number; status: string }) => void
}

export default function DocumentUpload({ onUploadComplete }: DocumentUploadProps) {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState("")
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      validateAndSetFile(selectedFile)
    }
  }

  const validateAndSetFile = (selectedFile: File) => {
    if (!selectedFile) return

    const allowedTypes = [".pdf", ".txt", ".md", ".docx"]
    const fileExtension = selectedFile.name.substring(selectedFile.name.lastIndexOf(".")).toLowerCase()

    if (!allowedTypes.includes(fileExtension)) {
      setError(`Unsupported file type. Allowed types: ${allowedTypes.join(", ")}`)
      return
    }

    setFile(selectedFile)
    setError("")
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile) {
      validateAndSetFile(droppedFile)
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    setProgress(0)
    setError("")

    try {
      const response = await uploadDocument(file, (progressValue) => {
        setProgress(progressValue)
      })

      setFile(null)
      setProgress(0)
      if (onUploadComplete) {
        onUploadComplete(response)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed. Please try again.")
    } finally {
      setUploading(false)
    }
  }

  const clearFile = () => {
    setFile(null)
    setError("")
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <div className="space-y-4">
      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          file ? "border-primary" : "border-muted-foreground hover:border-primary/50"
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onClick={() => fileInputRef.current?.click()}
      >
        {!file ? (
          <div className="flex flex-col items-center justify-center space-y-2">
            <Upload className="h-8 w-8 text-muted-foreground" />
            <p>Drag and drop a file or click to browse</p>
            <p className="text-sm text-muted-foreground">Supported formats: PDF, TXT, MD, DOCX</p>
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <File className="h-6 w-6" />
              <span className="truncate">{file.name}</span>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={(e) => {
                e.stopPropagation()
                clearFile()
              }}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        )}
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf,.txt,.md,.docx"
        />
      </div>

      {file && (
        <div className="space-y-2">
          {uploading && <Progress value={progress} className="h-2" />}
          <Button onClick={handleUpload} disabled={uploading} className="w-full">
            {uploading ? `Uploading (${progress}%)` : "Upload Document"}
          </Button>
        </div>
      )}
    </div>
  )
}

