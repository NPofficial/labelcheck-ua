'use client';

import { useState } from 'react';
import { ScanText, Copy, Check } from 'lucide-react';
import { CollapsibleSection } from './CollapsibleSection';

interface OcrTextSectionProps {
  fullText: string | null;
}

export function OcrTextSection({ fullText }: OcrTextSectionProps) {
  const [copied, setCopied] = useState(false);

  if (!fullText || fullText.trim().length === 0) {
    return null;
  }

  const lineCount = fullText.split('\n').length;
  const charCount = fullText.length;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(fullText);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard API не доступний — тихо ігноруємо.
    }
  };

  return (
    <CollapsibleSection
      title="Повний текст з етикетки (OCR)"
      icon={ScanText}
      subtitle={`${lineCount} рядків · ${charCount} символів`}
    >
      <div className="relative">
        <button
          onClick={handleCopy}
          className="absolute top-2 right-2 flex items-center gap-1.5 px-2 py-1 text-xs bg-white border border-border rounded-md hover:bg-gray-50 transition-colors"
          aria-label="Скопіювати текст"
        >
          {copied ? (
            <>
              <Check className="h-3 w-3 text-success" />
              Скопійовано
            </>
          ) : (
            <>
              <Copy className="h-3 w-3" />
              Копіювати
            </>
          )}
        </button>
        <pre className="text-xs font-mono text-foreground bg-gray-50 p-3 pr-24 rounded-lg overflow-x-auto whitespace-pre-wrap max-h-96 overflow-y-auto border border-border">
          {fullText}
        </pre>
      </div>
    </CollapsibleSection>
  );
}
