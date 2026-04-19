'use client';

import { useState, useEffect } from 'react';
import { FileText, File, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { formatFileSize, isImageFile, isPdfFile } from '@/lib/utils';

interface FilePreviewProps {
  file: File;
  onRemove: () => void;
}

export function FilePreview({ file, onRemove }: FilePreviewProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    // Only create preview URL for images
    if (isImageFile(file)) {
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    }
    return;
  }, [file]);

  return (
    <div className="flex items-center gap-4">
      {/* Preview/Icon */}
      <div className="flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden bg-gray-100 flex items-center justify-center">
        {isImageFile(file) && previewUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={previewUrl}
            alt={file.name}
            className="w-full h-full object-cover"
          />
        ) : isPdfFile(file) ? (
          <FileText className="h-10 w-10 text-red-500" />
        ) : (
          <File className="h-10 w-10 text-gray-400" />
        )}
      </div>

      {/* File Info */}
      <div className="flex-1 min-w-0">
        <p className="font-medium text-foreground truncate">{file.name}</p>
        <p className="text-sm text-muted-foreground">{formatFileSize(file.size)}</p>
        {isPdfFile(file) && (
          <p className="text-xs text-muted-foreground mt-1">PDF документ</p>
        )}
      </div>

      {/* Remove Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={onRemove}
        className="flex-shrink-0 hover:bg-red-50 hover:text-red-500"
        aria-label="Видалити файл"
      >
        <X className="h-5 w-5" />
      </Button>
    </div>
  );
}


