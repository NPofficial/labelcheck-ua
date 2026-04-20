'use client';

import { useState, useRef, useCallback, useId } from 'react';
import { Upload, Image as ImageIcon, Loader2, Camera } from 'lucide-react';
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
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const errorId = useId();

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
    if (inputRef.current) inputRef.current.value = '';
    if (cameraInputRef.current) cameraInputRef.current.value = '';
  }, []);

  const handleSubmit = useCallback(() => {
    if (selectedFile) {
      onFileSelect(selectedFile);
    }
  }, [selectedFile, onFileSelect]);

  const openFilePicker = useCallback(() => inputRef.current?.click(), []);
  const openCamera = useCallback(() => cameraInputRef.current?.click(), []);

  const handleZoneKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLDivElement>) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        openFilePicker();
      }
    },
    [openFilePicker]
  );

  const displayError = error || validationError;

  return (
    <div className="w-full max-w-2xl mx-auto">
      {!selectedFile ? (
        <div
          role="button"
          tabIndex={0}
          aria-label={content.checker.upload.title}
          aria-describedby={displayError ? errorId : undefined}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={openFilePicker}
          onKeyDown={handleZoneKeyDown}
          className={cn(
            'relative min-h-[300px] rounded-2xl border-2 border-dashed cursor-pointer transition-all',
            'flex flex-col items-center justify-center p-8',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2',
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
            aria-hidden="true"
            tabIndex={-1}
          />
          <input
            ref={cameraInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            onChange={handleInputChange}
            className="hidden"
            aria-hidden="true"
            tabIndex={-1}
          />

          <div className="text-center">
            <div
              className={cn(
                'w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4',
                isDragOver ? 'bg-primary/10' : 'bg-gray-100'
              )}
            >
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

            {/* Mobile-only camera button */}
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                openCamera();
              }}
              className={cn(
                'md:hidden mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-lg',
                'bg-primary text-white text-sm font-medium',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2'
              )}
            >
              <Camera className="h-4 w-4" />
              Зробити фото
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border p-6">
          <FilePreview file={selectedFile} onRemove={handleRemoveFile} />

          <div className="mt-6">
            <Button
              onClick={handleSubmit}
              disabled={isLoading}
              className="w-full bg-gradient-primary hover:opacity-90 text-white h-12 focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2"
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

      {displayError && (
        <div
          id={errorId}
          role="alert"
          className="mt-4 p-4 bg-error-light border border-error/20 rounded-xl"
        >
          <p className="text-error text-sm">{displayError}</p>
        </div>
      )}
    </div>
  );
}
