import { AlertTriangle } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';

interface WarningCardProps {
  warning: {
    field: string;
    message: string;
    source: string;
    penalty: number;
    recommendation?: string;
  };
}

export function WarningCard({ warning }: WarningCardProps) {
  return (
    <div className="rounded-xl border-l-4 border-l-warning bg-warning-light p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <AlertTriangle className="h-5 w-5 text-warning" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-medium text-foreground">{warning.field}</h4>
            {warning.penalty > 0 && (
              <span className="flex-shrink-0 text-sm font-semibold text-warning-700">
                {formatCurrency(warning.penalty)}
              </span>
            )}
          </div>
          <p className="text-sm text-muted-foreground mt-1">{warning.message}</p>
          <p className="text-xs text-muted-foreground mt-2">
            Джерело: {warning.source}
          </p>
          {warning.recommendation && (
            <div className="mt-3 p-3 bg-white/60 rounded-lg">
              <p className="text-xs font-medium text-foreground mb-1">
                Рекомендація:
              </p>
              <p className="text-sm text-muted-foreground">
                {warning.recommendation}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


