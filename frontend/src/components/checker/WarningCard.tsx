import { AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { DosageWarning, DosageErrorLevel } from '@/lib/types';

interface WarningCardProps {
  warning: DosageWarning;
}

const LEVEL_META: Record<DosageErrorLevel, { label: string; className: string }> = {
  0: { label: 'Заборонена речовина', className: 'bg-error text-white' },
  1: { label: 'EFSA Upper Limit', className: 'bg-error-600 text-white' },
  2: { label: 'EFSA Safe Level', className: 'bg-warning text-white' },
  3: { label: 'Таблиця 1 МОЗ', className: 'bg-warning-600 text-white' },
  4: { label: 'Додаток 3 МОЗ', className: 'bg-warning-700 text-white' },
};

export function WarningCard({ warning }: WarningCardProps) {
  const levelMeta = warning.level !== null ? LEVEL_META[warning.level] : null;
  const hasDoseInfo = warning.current_dose || warning.max_allowed;

  return (
    <div className="rounded-xl border-l-4 border-l-warning bg-warning-light p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <AlertTriangle className="h-5 w-5 text-warning" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 flex-wrap">
            <div className="flex items-center gap-2 flex-wrap">
              <h4 className="font-medium text-foreground">{warning.ingredient}</h4>
              {levelMeta && (
                <span
                  className={cn(
                    'text-xs px-2 py-0.5 rounded-full font-medium',
                    levelMeta.className
                  )}
                >
                  {levelMeta.label}
                </span>
              )}
            </div>
            <span className="flex-shrink-0 text-xs font-medium text-warning-700 bg-white/60 px-2 py-0.5 rounded-full">
              Можливий штраф
            </span>
          </div>

          <p className="text-sm text-muted-foreground mt-2">{warning.message}</p>

          {hasDoseInfo && (
            <div className="mt-3 p-3 bg-white/60 rounded-lg">
              <p className="text-xs font-medium text-foreground mb-1">Дозування:</p>
              <div className="text-sm text-muted-foreground space-y-0.5">
                {warning.current_dose && (
                  <p>
                    <span className="text-foreground">Поточна:</span>{' '}
                    {warning.current_dose}
                  </p>
                )}
                {warning.max_allowed && (
                  <p>
                    <span className="text-foreground">Максимально дозволена:</span>{' '}
                    {warning.max_allowed}
                  </p>
                )}
              </div>
            </div>
          )}

          {warning.recommendation && (
            <div className="mt-3 p-3 bg-white/60 rounded-lg">
              <p className="text-xs font-medium text-foreground mb-1">Рекомендація:</p>
              <p className="text-sm text-muted-foreground">{warning.recommendation}</p>
            </div>
          )}

          {warning.source && (
            <p className="text-xs text-muted-foreground mt-2">Джерело: {warning.source}</p>
          )}
        </div>
      </div>
    </div>
  );
}
