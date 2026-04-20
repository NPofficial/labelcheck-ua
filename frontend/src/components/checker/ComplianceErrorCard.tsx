import { Ban, FileWarning } from 'lucide-react';
import { cn, formatCurrency } from '@/lib/utils';
import type { ComplianceError } from '@/lib/types';

interface ComplianceErrorCardProps {
  error: ComplianceError;
}

const SEVERITY_LABELS: Record<string, { label: string; className: string }> = {
  critical: { label: 'Критична', className: 'bg-error text-white' },
  high: { label: 'Висока', className: 'bg-error-600 text-white' },
  medium: { label: 'Середня', className: 'bg-warning text-white' },
};

export function ComplianceErrorCard({ error }: ComplianceErrorCardProps) {
  if (error.type === 'forbidden_phrase') {
    return <ForbiddenPhraseCard error={error} />;
  }
  return <MandatoryFieldCard error={error} />;
}

function ForbiddenPhraseCard({ error }: { error: ComplianceError }) {
  const severity = error.severity
    ? SEVERITY_LABELS[error.severity] ?? {
        label: error.severity,
        className: 'bg-muted text-foreground',
      }
    : null;

  return (
    <div className="rounded-xl border-l-4 border-l-error bg-error-light p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <Ban className="h-5 w-5 text-error" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-medium text-foreground">Заборонена фраза</h4>
              {severity && (
                <span
                  className={cn(
                    'text-xs px-2 py-0.5 rounded-full font-medium',
                    severity.className
                  )}
                >
                  {severity.label}
                </span>
              )}
              {error.category && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-white/60 text-muted-foreground">
                  {error.category}
                </span>
              )}
            </div>
            <span className="flex-shrink-0 text-sm font-semibold text-error">
              {formatCurrency(error.penalty_amount)}
            </span>
          </div>

          {error.phrase && (
            <div className="mt-2 p-2 bg-white/60 rounded border border-error/20">
              <p className="text-sm text-foreground italic">«{error.phrase}»</p>
            </div>
          )}

          <p className="text-sm text-muted-foreground mt-2">{error.error_message}</p>

          {error.explanation && (
            <p className="text-xs text-muted-foreground mt-1">{error.explanation}</p>
          )}

          <div className="mt-3 p-3 bg-white/60 rounded-lg">
            <p className="text-xs font-medium text-foreground mb-1">Рекомендація:</p>
            <p className="text-sm text-muted-foreground">{error.recommendation}</p>
          </div>

          <p className="text-xs text-muted-foreground mt-2">
            Джерело: {error.regulatory_source}
            {error.article_number ? `, ст. ${error.article_number}` : ''}
          </p>
        </div>
      </div>
    </div>
  );
}

function MandatoryFieldCard({ error }: { error: ComplianceError }) {
  return (
    <div className="rounded-xl border-l-4 border-l-error bg-error-light p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <FileWarning className="h-5 w-5 text-error" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-medium text-foreground">
                Відсутнє обов&apos;язкове поле
              </h4>
              {error.field_name && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-white/60 text-foreground font-medium">
                  {error.field_name}
                </span>
              )}
            </div>
            <span className="flex-shrink-0 text-sm font-semibold text-error">
              {formatCurrency(error.penalty_amount)}
            </span>
          </div>

          <p className="text-sm text-muted-foreground mt-2">{error.error_message}</p>

          {error.explanation && (
            <p className="text-xs text-muted-foreground mt-1">{error.explanation}</p>
          )}

          <div className="mt-3 p-3 bg-white/60 rounded-lg">
            <p className="text-xs font-medium text-foreground mb-1">Рекомендація:</p>
            <p className="text-sm text-muted-foreground">{error.recommendation}</p>
          </div>

          <p className="text-xs text-muted-foreground mt-2">
            Джерело: {error.regulatory_source}
            {error.article_number ? `, ст. ${error.article_number}` : ''}
          </p>
        </div>
      </div>
    </div>
  );
}
