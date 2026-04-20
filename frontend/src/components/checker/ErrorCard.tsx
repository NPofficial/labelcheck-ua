import { XCircle } from 'lucide-react';
import { cn, formatCurrency } from '@/lib/utils';
import { formatDosageSource } from '@/lib/labels';
import type { DosageError, DosageErrorLevel } from '@/lib/types';

interface ErrorCardProps {
  error: DosageError;
}

const LEVEL_META: Record<DosageErrorLevel, { label: string; className: string }> = {
  0: { label: 'Заборонена речовина', className: 'bg-error text-white' },
  1: { label: 'EFSA Upper Limit', className: 'bg-error-600 text-white' },
  2: { label: 'EFSA Safe Level', className: 'bg-warning text-white' },
  3: { label: 'Таблиця 1 МОЗ', className: 'bg-warning-600 text-white' },
  4: { label: 'Додаток 3 МОЗ', className: 'bg-warning-700 text-white' },
};

export function ErrorCard({ error }: ErrorCardProps) {
  const levelMeta = LEVEL_META[error.level];
  const hasDoseInfo = error.current_dose || error.max_allowed;
  const hasFormInfo =
    error.current_form || (error.allowed_forms && error.allowed_forms.length > 0);

  return (
    <div className="rounded-xl border-l-4 border-l-error bg-error-light p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <XCircle className="h-5 w-5 text-error" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-medium text-foreground">{error.ingredient}</h4>
              <span
                className={cn(
                  'text-xs px-2 py-0.5 rounded-full font-medium',
                  levelMeta.className
                )}
              >
                {levelMeta.label}
              </span>
            </div>
            <span className="flex-shrink-0 text-sm font-semibold text-error">
              {formatCurrency(error.penalty_amount)}
            </span>
          </div>

          <p className="text-sm text-muted-foreground mt-2">{error.message}</p>

          {hasDoseInfo && (
            <div className="mt-3 p-3 bg-white/60 rounded-lg">
              <p className="text-xs font-medium text-foreground mb-1">Дозування:</p>
              <div className="text-sm text-muted-foreground space-y-0.5">
                {error.current_dose && (
                  <p>
                    <span className="text-foreground">Поточна:</span> {error.current_dose}
                  </p>
                )}
                {error.max_allowed && (
                  <p>
                    <span className="text-foreground">Максимально дозволена:</span>{' '}
                    {error.max_allowed}
                  </p>
                )}
                {error.three_times_limit && (
                  <p className="text-xs">
                    <span className="text-foreground">Потрійний ліміт:</span>{' '}
                    {error.three_times_limit}
                  </p>
                )}
              </div>
            </div>
          )}

          {hasFormInfo && (
            <div className="mt-2 p-3 bg-white/60 rounded-lg">
              <p className="text-xs font-medium text-foreground mb-1">Форма речовини:</p>
              <div className="text-sm text-muted-foreground space-y-0.5">
                {error.current_form && (
                  <p>
                    <span className="text-foreground">Поточна:</span> {error.current_form}
                  </p>
                )}
                {error.allowed_forms && error.allowed_forms.length > 0 && (
                  <p>
                    <span className="text-foreground">Дозволені:</span>{' '}
                    {error.allowed_forms.join(', ')}
                  </p>
                )}
              </div>
            </div>
          )}

          <div className="mt-3 p-3 bg-white/60 rounded-lg">
            <p className="text-xs font-medium text-foreground mb-1">Рекомендація:</p>
            <p className="text-sm text-muted-foreground">{error.recommendation}</p>
          </div>

          <p className="text-xs text-muted-foreground mt-2">
            Джерело: {error.regulatory_source}
            {error.source ? ` · ${formatDosageSource(error.source)}` : ''}
          </p>
        </div>
      </div>
    </div>
  );
}
