"use client"

import { useState } from "react"
import { ProtectedRoute } from "@/components/protected-route"
import DocumentUpload from "@/components/documents/DocumentUpload"
import DocumentList from "@/components/documents/DocumentList"

export default function DocumentsPage() {
  const [refreshKey, setRefreshKey] = useState(0)

  const handleUploadComplete = () => {
    // Trigger refresh of document list
    setRefreshKey((prev) => prev + 1)
  }

  const handleDocumentDeleted = () => {
    // Document list will refresh itself, but we can add additional logic here if needed
  }

  return (
    <ProtectedRoute>
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <h1 className="text-2xl font-bold mb-6">Documents</h1>
        <p className="text-muted-foreground mb-8">
          Upload documents to enable document-aware responses in your chat conversations.
        </p>

        <div className="space-y-8">
          <div>
            <h2 className="text-xl font-semibold mb-4">Upload Document</h2>
            <DocumentUpload onUploadComplete={handleUploadComplete} />
          </div>

          <div>
            <DocumentList key={refreshKey} onDocumentDeleted={handleDocumentDeleted} />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  )
}

