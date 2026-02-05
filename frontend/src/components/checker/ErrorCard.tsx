import { XCircle } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';

interface ErrorCardProps {
  error: {
    field: string;
    message: string;
    source: string;
    penalty: number;
    recommendation?: string;
  };
}

export function ErrorCard({ error }: ErrorCardProps) {
  return (
    <div className="rounded-xl border-l-4 border-l-error bg-error-light p-4">
      <div className="flex items-start gap-3">
        <div className="flex-shrink-0 mt-0.5">
          <XCircle className="h-5 w-5 text-error" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className="font-medium text-foreground">{error.field}</h4>
            <span className="flex-shrink-0 text-sm font-semibold text-error">
              {formatCurrency(error.penalty)}
            </span>
          </div>
          <p className="text-sm text-muted-foreground mt-1">{error.message}</p>
          <p className="text-xs text-muted-foreground mt-2">
            Джерело: {error.source}
          </p>
          {error.recommendation && (
            <div className="mt-3 p-3 bg-white/60 rounded-lg">
              <p className="text-xs font-medium text-foreground mb-1">
                Рекомендація:
              </p>
              <p className="text-sm text-muted-foreground">
                {error.recommendation}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


