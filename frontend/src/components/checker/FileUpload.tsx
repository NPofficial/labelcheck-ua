"use client"

import { useState, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { LoadingSpinner } from "@/components/common/LoadingSpinner"
import { MAX_FILE_SIZE, ACCEPTED_FILE_TYPES } from "@/lib/constants"

interface FileUploadProps {
  onFileSelect: (file: File) => void
  onUpload: (file: File) => Promise<void>
}

export function FileUpload({ onFileSelect, onUpload }: FileUploadProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [error, setError] = useState<string>("")
  const [isUploading, setIsUploading] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const validateFile = (file: File): boolean => {
    if (file.size > MAX_FILE_SIZE) {
      setError("Файл занадто великий. Максимальний розмір: 10MB")
      return false
    }

    if (!ACCEPTED_FILE_TYPES.includes(file.type as never)) {
      setError("Непідтримуваний формат файлу. Використовуйте JPG, PNG або PDF")
      return false
    }

    return true
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    setError("")

    if (validateFile(file)) {
      setSelectedFile(file)
      onFileSelect(file)
    } else {
      setSelectedFile(null)
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setIsUploading(true)
    setError("")

    try {
      await onUpload(selectedFile)
    } catch (err) {
      setError(err instanceof Error ? err.message : "Помилка завантаження")
    } finally {
      setIsUploading(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const file = e.dataTransfer.files[0]
    if (file && validateFile(file)) {
      setSelectedFile(file)
      onFileSelect(file)
    }
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
  }

  return (
    <div className="space-y-4">
      <div
        className="rounded-lg border-2 border-dashed border-muted-foreground/25 p-8 text-center transition-colors hover:border-primary/50"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept={ACCEPTED_FILE_TYPES.join(",")}
          onChange={handleFileChange}
          className="hidden"
        />

        <div className="space-y-2">
          <p className="text-sm text-muted-foreground">
            Перетягніть файл сюди або
          </p>
          <Button
            type="button"
            variant="outline"
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
          >
            Оберіть файл
          </Button>
          <p className="text-xs text-muted-foreground">
            JPG, PNG або PDF (макс. 10MB)
          </p>
        </div>
      </div>

      {selectedFile && (
        <div className="rounded-lg border bg-muted/50 p-4">
          <p className="text-sm">
            <span className="font-medium">Обрано:</span> {selectedFile.name}
          </p>
          <p className="text-xs text-muted-foreground">
            Розмір: {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
          </p>
        </div>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <Button
        onClick={handleUpload}
        disabled={!selectedFile || isUploading}
        className="w-full"
      >
        {isUploading ? (
          <>
            <LoadingSpinner size="sm" className="mr-2" />
            Завантаження...
          </>
        ) : (
          "Перевірити"
        )}
      </Button>
    </div>
  )
}

