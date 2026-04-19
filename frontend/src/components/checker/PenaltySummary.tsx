import { AlertCircle } from 'lucide-react';
import { formatCurrency } from '@/lib/utils';
import { content } from '@/content/ua';

interface PenaltySummaryProps {
  totalPenalty: number;
  errorCount: number;
  warningCount: number;
}

export function PenaltySummary({
  totalPenalty,
  errorCount,
  warningCount,
}: PenaltySummaryProps) {
  return (
    <div className="rounded-2xl bg-gradient-to-br from-error to-error-600 p-6 text-white">
      <div className="flex items-start gap-4">
        <div className="flex-shrink-0">
          <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center">
            <AlertCircle className="h-6 w-6" />
          </div>
        </div>
        <div className="flex-1">
          <p className="text-white/80 text-sm font-medium mb-1">
            {content.checker.results.totalPenalty}
          </p>
          <p className="text-3xl md:text-4xl font-bold">
            {formatCurrency(totalPenalty)}
          </p>
        </div>
      </div>

      {/* Breakdown */}
      <div className="mt-6 pt-4 border-t border-white/20">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-white/60 text-xs mb-1">Критичних помилок</p>
            <p className="text-xl font-semibold">{errorCount}</p>
          </div>
          <div>
            <p className="text-white/60 text-xs mb-1">Попереджень</p>
            <p className="text-xl font-semibold">{warningCount}</p>
          </div>
        </div>
      </div>

      {/* Disclaimer */}
      <p className="mt-4 text-xs text-white/60">
        * Сума штрафу є орієнтовною та може відрізнятися залежно від обставин
      </p>
    </div>
  );
}


