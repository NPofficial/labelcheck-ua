'use client';

import { useState, useRef, useCallback } from 'react';
import { Upload, Image as ImageIcon, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn, validateFile } from '@/lib/utils';
import { content } from '@/content/ua';
import { FilePreview } from './FilePreview';

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  isLoading?: boolean;
  error?: string;
}

export function UploadZone({ onFileSelect, isLoading, error }: UploadZoneProps) {
  const [isDragOver, setIsDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((file: File) => {
    const validation = validateFile(file);
    if (!validation.valid) {
      setValidationError(validation.error || null);
      setSelectedFile(null);
      return;
    }
    setValidationError(null);
    setSelectedFile(file);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) {
        handleFile(file);
      }
    },
    [handleFile]
  );

  const handleRemoveFile = useCallback(() => {
    setSelectedFile(null);
    setValidationError(null);
    if (inputRef.current) {
      inputRef.current.value = '';
    }
  }, []);

  const handleSubmit = useCallback(() => {
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  }, [selectedFile, onFileSelect]);

  const displayError = error || validationError;

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!selectedFile ? (
        // Upload Zone
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={cn(
            'relative min-h-[300px] rounded-2xl border-2 border-dashed cursor-pointer transition-all',
            'flex flex-col items-center justify-center p-8',
            isDragOver
              ? 'border-primary bg-primary/5'
              : 'border-gray-300 bg-white hover:border-primary/50 hover:bg-gray-50',
            displayError && 'border-error bg-error-light'
          )}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,application/pdf"
            onChange={handleInputChange}
            className="hidden"
          />

          <div className="text-center">
            <div className={cn(
              'w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4',
              isDragOver ? 'bg-primary/10' : 'bg-gray-100'
            )}>
              {isDragOver ? (
                <ImageIcon className="h-8 w-8 text-primary" />
              ) : (
                <Upload className="h-8 w-8 text-gray-400" />
              )}
            </div>

            <h3 className="text-lg font-medium text-foreground mb-2">
              {isDragOver
                ? content.checker.upload.dragActive
                : content.checker.upload.title}
            </h3>
            <p className="text-muted-foreground mb-4">
              {content.checker.upload.subtitle}
            </p>
            <p className="text-sm text-muted-foreground">
              {content.checker.upload.formats}
            </p>
          </div>
        </div>
      ) : (
        // File Preview
        <div className="bg-white rounded-2xl border p-6">
          <FilePreview file={selectedFile} onRemove={handleRemoveFile} />
          
          <div className="mt-6">
            <Button
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full bg-gradient-primary hover:opacity-90 text-white h-12"
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  {content.common.loading}
                </>
              ) : (
                content.header.cta
              )}
            </Button>
          </div>
        </div>
      )}

      {/* Error Message */}
      {displayError && (
        <div className="mt-4 p-4 bg-error-light border border-error/20 rounded-xl">
          <p className="text-error text-sm">{displayError}</p>
        </div>
      )}
    </div>
  );
}


