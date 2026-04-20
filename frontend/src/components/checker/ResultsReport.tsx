'use client';

import {
  XCircle,
  AlertTriangle,
  Ban,
  FileWarning,
  Download,
  Mail,
  Share2,
  RefreshCw,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { content } from '@/content/ua';
import type { FullCheckResponse } from '@/lib/types';
import { ErrorCard } from './ErrorCard';
import { WarningCard } from './WarningCard';
import { ComplianceErrorCard } from './ComplianceErrorCard';
import { PenaltySummary } from './PenaltySummary';
import { StatusHero } from './StatusHero';

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
  const dosageErrors = result.errors ?? [];
  const dosageWarnings = result.warnings ?? [];
  const complianceErrors = result.compliance_errors ?? [];
  const totalPenalty = result.penalties?.total_amount ?? 0;

  const forbiddenPhrases = complianceErrors.filter((e) => e.type === 'forbidden_phrase');
  const missingFields = complianceErrors.filter((e) => e.type === 'mandatory_field');

  const totalErrorCount = dosageErrors.length + complianceErrors.length;
  const totalWarningCount = dosageWarnings.length;
  const totalIngredients = result.stats?.total_ingredients ?? 0;

  const hasAnyErrors = totalErrorCount > 0;
  const hasAnyWarnings = totalWarningCount > 0;

  return (
    <div className="w-full max-w-3xl mx-auto">
      <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
        <StatusHero result={result} />

        {/* Summary Stats — нейтральні лічильники */}
        <div className="grid grid-cols-3 border-b">
          <div className="p-4 text-center border-r">
            <p className="text-2xl font-bold text-error">{totalErrorCount}</p>
            <p className="text-xs text-muted-foreground">
              {content.checker.results.errors}
            </p>
          </div>
          <div className="p-4 text-center border-r">
            <p className="text-2xl font-bold text-warning">{totalWarningCount}</p>
            <p className="text-xs text-muted-foreground">
              {content.checker.results.warnings}
            </p>
          </div>
          <div className="p-4 text-center">
            <p className="text-2xl font-bold text-foreground">{totalIngredients}</p>
            <p className="text-xs text-muted-foreground">Проаналізовано</p>
          </div>
        </div>

        <div className="p-6 pb-24 md:pb-6 space-y-6">
          {(hasAnyErrors || hasAnyWarnings) && totalPenalty > 0 && (
            <PenaltySummary
              totalPenalty={totalPenalty}
              errorCount={totalErrorCount}
              warningCount={totalWarningCount}
            />
          )}

          {/* Dosage Errors */}
          {dosageErrors.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <XCircle className="h-5 w-5 text-error" />
                Помилки дозування ({dosageErrors.length})
              </h3>
              <div className="space-y-3">
                {dosageErrors.map((error, index) => (
                  <ErrorCard key={`dosage-err-${index}`} error={error} />
                ))}
              </div>
            </section>
          )}

          {/* Forbidden Phrases */}
          {forbiddenPhrases.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <Ban className="h-5 w-5 text-error" />
                Заборонені фрази ({forbiddenPhrases.length})
              </h3>
              <div className="space-y-3">
                {forbiddenPhrases.map((error, index) => (
                  <ComplianceErrorCard key={`phrase-${index}`} error={error} />
                ))}
              </div>
            </section>
          )}

          {/* Missing Mandatory Fields */}
          {missingFields.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <FileWarning className="h-5 w-5 text-error" />
                Відсутні обов&apos;язкові поля ({missingFields.length})
              </h3>
              <div className="space-y-3">
                {missingFields.map((error, index) => (
                  <ComplianceErrorCard key={`field-${index}`} error={error} />
                ))}
              </div>
            </section>
          )}

          {/* Dosage Warnings */}
          {dosageWarnings.length > 0 && (
            <section>
              <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-warning" />
                {content.checker.results.warnings} ({dosageWarnings.length})
              </h3>
              <div className="space-y-3">
                {dosageWarnings.map((warning, index) => (
                  <WarningCard key={`warn-${index}`} warning={warning} />
                ))}
              </div>
            </section>
          )}
        </div>

        {/* Action Buttons — Sticky on Mobile */}
        <div className="sticky bottom-0 left-0 right-0 md:static bg-white border-t md:border-0 p-4 md:px-6 md:pb-6 shadow-up md:shadow-none">
          <div className="flex flex-col sm:flex-row gap-3">
            <Button
              onClick={onDownloadPdf}
              className="flex-1 bg-gradient-primary hover:opacity-90 text-white"
            >
              <Download className="mr-2 h-4 w-4" />
              {content.checker.results.downloadPdf}
            </Button>
            <Button onClick={onCheckAnother} variant="outline" className="flex-1">
              <RefreshCw className="mr-2 h-4 w-4" />
              {content.checker.results.checkAnother}
            </Button>
          </div>
          <div className="flex gap-3 mt-3">
            <Button onClick={onSendEmail} variant="ghost" size="sm" className="flex-1">
              <Mail className="mr-2 h-4 w-4" />
              {content.checker.results.sendEmail}
            </Button>
            <Button onClick={onShare} variant="ghost" size="sm" className="flex-1">
              <Share2 className="mr-2 h-4 w-4" />
              {content.checker.results.share}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
