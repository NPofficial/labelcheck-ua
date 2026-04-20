import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';
import { cn, formatCurrency } from '@/lib/utils';
import { computeOverallStatus, type FullCheckResponse, type OverallStatus } from '@/lib/types';

interface StatusHeroProps {
  result: FullCheckResponse;
}

interface StatusConfig {
  icon: typeof CheckCircle2;
  iconBg: string;
  iconColor: string;
  bg: string;
  title: string;
  subtitle: string;
  titleColor: string;
}

function buildConfig(status: OverallStatus, result: FullCheckResponse): StatusConfig {
  const errorCount = result.errors.length + result.compliance_errors.length;
  const warningCount = result.warnings.length;
  const penalty = result.penalties.total_amount;

  switch (status) {
    case 'valid':
      return {
        icon: CheckCircle2,
        iconBg: 'bg-success',
        iconColor: 'text-white',
        bg: 'bg-success-light',
        titleColor: 'text-success',
        title: 'Етикетка відповідає вимогам',
        subtitle: 'Критичних порушень не виявлено.',
      };
    case 'warnings_only':
      return {
        icon: AlertTriangle,
        iconBg: 'bg-warning',
        iconColor: 'text-white',
        bg: 'bg-warning-light',
        titleColor: 'text-warning-700',
        title: 'Є попередження',
        subtitle: `Знайдено попереджень: ${warningCount}. Критичних помилок немає.`,
      };
    case 'has_errors':
      return {
        icon: XCircle,
        iconBg: 'bg-error',
        iconColor: 'text-white',
        bg: 'bg-error-light',
        titleColor: 'text-error',
        title: 'Виявлено порушення',
        subtitle:
          penalty > 0
            ? `Критичних помилок: ${errorCount}. Потенційний штраф: ${formatCurrency(penalty)}.`
            : `Критичних помилок: ${errorCount}.`,
      };
  }
}

export function StatusHero({ result }: StatusHeroProps) {
  const status = computeOverallStatus(result);
  const config = buildConfig(status, result);
  const Icon = config.icon;

  return (
    <div className={cn('p-6 text-center', config.bg)}>
      <div className="flex justify-center mb-4">
        <div
          className={cn(
            'w-16 h-16 rounded-full flex items-center justify-center',
            config.iconBg
          )}
        >
          <Icon className={cn('h-8 w-8', config.iconColor)} />
        </div>
      </div>
      <h2 className="text-2xl font-bold text-foreground">Результати перевірки</h2>
      <p className={cn('mt-2 font-medium', config.titleColor)}>{config.title}</p>
      <p className="mt-1 text-sm text-muted-foreground">{config.subtitle}</p>
    </div>
  );
}
