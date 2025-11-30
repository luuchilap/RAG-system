"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@workspace/ui/components/card"
import { Button } from "@workspace/ui/components/button"
import { Alert, AlertDescription } from "@workspace/ui/components/alert"
import { Trash2 } from "lucide-react"
import { getDocuments, deleteDocument, type Document } from "@/lib/api"

interface DocumentListProps {
  onDocumentDeleted?: () => void
}

export default function DocumentList({ onDocumentDeleted }: DocumentListProps) {
  const [documents, setDocuments] = useState<Document[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [deletingId, setDeletingId] = useState<string | null>(null)

  useEffect(() => {
    fetchDocuments()
  }, [])

  const fetchDocuments = async () => {
    try {
      setLoading(true)
      setError("")
      const data = await getDocuments()
      setDocuments(data.documents)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch documents")
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (documentId: string) => {
    if (!confirm("Are you sure you want to delete this document?")) {
      return
    }

    try {
      setDeletingId(documentId)
      await deleteDocument(documentId)
      setDocuments(documents.filter((doc) => doc.id !== documentId))
      if (onDocumentDeleted) {
        onDocumentDeleted()
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to delete document")
    } finally {
      setDeletingId(null)
    }
  }

  const formatFileSize = (bytes: number | null): string => {
    if (!bytes) return "Unknown"
    if (bytes < 1024) return `${bytes} bytes`
    else if (bytes < 1048576) return `${(bytes / 1024).toFixed(1)} KB`
    else return `${(bytes / 1048576).toFixed(1)} MB`
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString()
  }

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-bold">Your Documents</h2>

      {loading ? (
        <p className="text-muted-foreground">Loading documents...</p>
      ) : error ? (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : documents.length === 0 ? (
        <p className="text-muted-foreground">No documents uploaded yet.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {documents.map((doc) => (
            <Card key={doc.id}>
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-base truncate flex-1 mr-2">{doc.filename}</CardTitle>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 flex-shrink-0"
                    onClick={() => handleDelete(doc.id)}
                    disabled={deletingId === doc.id}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-sm space-y-1">
                  <p>
                    <span className="font-medium">Type:</span> {doc.file_type.toUpperCase()}
                  </p>
                  <p>
                    <span className="font-medium">Size:</span> {formatFileSize(doc.file_size)}
                  </p>
                  <p>
                    <span className="font-medium">Chunks:</span> {doc.chunk_count ?? "N/A"}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    <span className="font-medium">Uploaded:</span> {formatDate(doc.uploaded_at)}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  )
}

