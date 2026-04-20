'use client';

import { CheckCircle, Loader2, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { content } from '@/content/ua';

interface ProgressStepperProps {
  currentStep: 1 | 2;
  /** Якщо передано — рендериться кнопка "Скасувати". */
  onCancel?: () => void;
  /** Назва файлу — щоб користувач бачив що саме обробляється. */
  fileName?: string;
}

interface StepDef {
  number: 1 | 2;
  title: string;
  description: string;
  /** Орієнтовний час етапу (для UX-очікування). */
  approxSeconds: number;
}

const STEPS: StepDef[] = [
  {
    number: 1,
    title: content.checker.progress.step1,
    description: content.checker.progress.step1Description,
    approxSeconds: 35,
  },
  {
    number: 2,
    title: content.checker.progress.step2,
    description: content.checker.progress.step2Description,
    approxSeconds: 15,
  },
];

export function ProgressStepper({ currentStep, onCancel, fileName }: ProgressStepperProps) {
  const getStepState = (stepNumber: number) => {
    if (stepNumber < currentStep) return 'completed';
    if (stepNumber === currentStep) return 'active';
    return 'pending';
  };

  return (
    <div className="w-full max-w-xl mx-auto p-6 bg-white rounded-2xl border">
      {fileName && (
        <p className="text-sm text-muted-foreground mb-4 truncate" title={fileName}>
          Обробляється: <span className="text-foreground">{fileName}</span>
        </p>
      )}

      <div className="space-y-6">
        {STEPS.map((step, index) => {
          const state = getStepState(step.number);
          const isLast = index === STEPS.length - 1;

          return (
            <div key={step.number} className="relative">
              <div className="flex items-start gap-4">
                <div className="flex-shrink-0">
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center transition-all',
                      state === 'completed' && 'bg-success text-white',
                      state === 'active' && 'bg-primary text-white',
                      state === 'pending' && 'bg-gray-100 text-gray-400'
                    )}
                  >
                    {state === 'completed' ? (
                      <CheckCircle className="h-5 w-5" />
                    ) : state === 'active' ? (
                      <Loader2 className="h-5 w-5 animate-spin" />
                    ) : (
                      <span className="text-sm font-medium">{step.number}</span>
                    )}
                  </div>
                </div>

                <div className="flex-1 pb-6">
                  <div className="flex items-baseline gap-2 flex-wrap">
                    <h4
                      className={cn(
                        'font-medium',
                        state === 'pending' ? 'text-gray-400' : 'text-foreground'
                      )}
                    >
                      {step.title}
                    </h4>
                    <span
                      className={cn(
                        'text-xs',
                        state === 'pending' ? 'text-gray-300' : 'text-muted-foreground'
                      )}
                    >
                      ~{step.approxSeconds} сек
                    </span>
                  </div>
                  <p
                    className={cn(
                      'text-sm mt-1',
                      state === 'pending' ? 'text-gray-300' : 'text-muted-foreground'
                    )}
                  >
                    {step.description}
                  </p>

                  {state === 'active' && (
                    <div className="mt-3">
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div className="h-full w-1/3 bg-gradient-primary rounded-full animate-indeterminate" />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {!isLast && (
                <div
                  className={cn(
                    'absolute left-5 top-10 w-0.5 h-[calc(100%-2.5rem)]',
                    state === 'completed' ? 'bg-success' : 'bg-gray-200'
                  )}
                />
              )}
            </div>
          );
        })}
      </div>

      {onCancel && (
        <div className="mt-2 pt-4 border-t border-border">
          <Button
            onClick={onCancel}
            variant="ghost"
            className="w-full text-muted-foreground hover:text-error"
          >
            <X className="mr-2 h-4 w-4" />
            {content.common.cancel}
          </Button>
          <p className="text-xs text-muted-foreground text-center mt-2">
            Або натисніть Esc
          </p>
        </div>
      )}
    </div>
  );
}
