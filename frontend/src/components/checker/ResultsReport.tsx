'use client';

import { useState } from 'react';
import { 
  CheckCircle, 
  XCircle, 
  Download, 
  Mail, 
  Share2, 
  RefreshCw,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { content } from '@/content/ua';
import type { FullCheckResponse } from '@/lib/api-client';
import { ErrorCard } from './ErrorCard';
import { WarningCard } from './WarningCard';
import { PenaltySummary } from './PenaltySummary';

interface ResultsReportProps {
  result: FullCheckResponse;
  onDownloadPdf: () => void;
  onSendEmail: () => void;
  onShare: () => void;
  onCheckAnother: () => void;
}

export function ResultsReport({
  result,
  onDownloadPdf,
  onSendEmail,
  onShare,
  onCheckAnother,
}: ResultsReportProps) {
  const [showCorrectItems, setShowCorrectItems] = useState(false);

  const hasErrors = result.errors.length > 0;
  const hasWarnings = result.warnings.length > 0;
  const correctCount = result.mandatory_fields.present.length;

  return (
    <div className="w-full max-w-3xl mx-auto">
      {/* Main Card */}
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        {/* Header */}
        <div
          className={cn(
            'p-6 text-center',
            result.is_valid ? 'bg-success-light' : 'bg-error-light'
          )}
        >
          <div className="flex justify-center mb-4">
            {result.is_valid ? (
              <div className="w-16 h-16 rounded-full bg-success flex items-center justify-center">
                <CheckCircle className="h-8 w-8 text-white" />
              </div>
            ) : (
              <div className="w-16 h-16 rounded-full bg-error flex items-center justify-center">
                <XCircle className="h-8 w-8 text-white" />
              </div>
            )}
          </div>
          <h2 className="text-2xl font-bold text-foreground">
            {content.checker.results.title}
          </h2>
          <p
            className={cn(
              'mt-2 font-medium',
              result.is_valid ? 'text-success' : 'text-error'
            )}
          >
            {result.is_valid
              ? content.checker.results.valid
              : content.checker.results.invalid}
          </p>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-3 border-b">
          <div className="p-4 text-center border-r">
            <p className="text-2xl font-bold text-error">{result.errors.length}</p>
            <p className="text-xs text-muted-foreground">
              {content.checker.results.errors}
            </p>
          </div>
          <div className="p-4 text-center border-r">
            <p className="text-2xl font-bold text-warning">{result.warnings.length}</p>
            <p className="text-xs text-muted-foreground">
              {content.checker.results.warnings}
            </p>
          </div>
          <div className="p-4 text-center">
            <p className="text-2xl font-bold text-success">{correctCount}</p>
            <p className="text-xs text-muted-foreground">
              {content.checker.results.correct}
            </p>
          </div>
        </div>

        {/* Content */}
        <div className="p-6 pb-24 md:pb-6 space-y-6">
          {/* Penalty Summary */}
          {(hasErrors || hasWarnings) && (
            <PenaltySummary
              totalPenalty={result.penalties.total}
              errorCount={result.errors.length}
              warningCount={result.warnings.length}
            />
          )}

          {/* Errors Section */}
          {hasErrors && (
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <XCircle className="h-5 w-5 text-error" />
                {content.checker.results.errors} ({result.errors.length})
              </h3>
              <div className="space-y-3">
                {result.errors.map((error, index) => (
                  <ErrorCard key={index} error={error} />
                ))}
              </div>
            </div>
          )}

          {/* Warnings Section */}
          {hasWarnings && (
            <div>
              <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <XCircle className="h-5 w-5 text-warning" />
                {content.checker.results.warnings} ({result.warnings.length})
              </h3>
              <div className="space-y-3">
                {result.warnings.map((warning, index) => (
                  <WarningCard key={index} warning={warning} />
                ))}
              </div>
            </div>
          )}

          {/* Correct Items Section (Collapsible) */}
          {correctCount > 0 && (
            <div>
              <button
                onClick={() => setShowCorrectItems(!showCorrectItems)}
                className="w-full flex items-center justify-between p-4 bg-success-light rounded-xl hover:bg-success-100 transition-colors"
              >
                <span className="flex items-center gap-2 font-medium text-foreground">
                  <CheckCircle className="h-5 w-5 text-success" />
                  {content.checker.results.correct} ({correctCount})
                </span>
                {showCorrectItems ? (
                  <ChevronUp className="h-5 w-5 text-muted-foreground" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-muted-foreground" />
                )}
              </button>
              {showCorrectItems && (
                <div className="mt-3 space-y-2">
                  {result.mandatory_fields.present.map((field, index) => (
                    <div
                      key={index}
                      className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg"
                    >
                      <CheckCircle className="h-4 w-4 text-success" />
                      <span className="text-sm text-foreground">{field}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Forbidden Phrases */}
          {result.forbidden_phrases.found.length > 0 && (
            <div className="p-4 bg-error-light rounded-xl">
              <h4 className="font-medium text-foreground mb-2">
                Виявлені заборонені фрази:
              </h4>
              <ul className="space-y-1">
                {result.forbidden_phrases.found.map((phrase, index) => (
                  <li key={index} className="text-sm text-error flex items-start gap-2">
                    <span>•</span>
                    <span>{phrase}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Action Buttons - Sticky on Mobile */}
        <div className="sticky bottom-0 left-0 right-0 md:static bg-white border-t md:border-0 p-4 md:px-6 md:pb-6 shadow-up md:shadow-none">
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={onDownloadPdf}
              className="flex-1 bg-gradient-primary hover:opacity-90 text-white"
            >
              <Download className="mr-2 h-4 w-4" />
              {content.checker.results.downloadPdf}
            </Button>
            <Button
              onClick={onCheckAnother}
              variant="outline"
              className="flex-1"
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              {content.checker.results.checkAnother}
            </Button>
          </div>
          <div className="flex gap-3 mt-3">
            <Button
              onClick={onSendEmail}
              variant="ghost"
              size="sm"
              className="flex-1"
            >
              <Mail className="mr-2 h-4 w-4" />
              {content.checker.results.sendEmail}
            </Button>
            <Button
              onClick={onShare}
              variant="ghost"
              size="sm"
              className="flex-1"
            >
              <Share2 className="mr-2 h-4 w-4" />
              {content.checker.results.share}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}


