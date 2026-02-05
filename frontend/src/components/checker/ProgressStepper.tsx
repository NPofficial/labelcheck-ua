'use client';

import { CheckCircle, Loader2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { content } from '@/content/ua';

interface ProgressStepperProps {
  currentStep: 1 | 2;
  step1Progress: number;
  step2Progress: number;
}

export function ProgressStepper({
  currentStep,
  step1Progress,
  step2Progress,
}: ProgressStepperProps) {
  const steps = [
    {
      number: 1,
      title: content.checker.progress.step1,
      description: content.checker.progress.step1Description,
      progress: step1Progress,
    },
    {
      number: 2,
      title: content.checker.progress.step2,
      description: content.checker.progress.step2Description,
      progress: step2Progress,
    },
  ];

  const getStepState = (stepNumber: number) => {
    if (stepNumber < currentStep) return 'completed';
    if (stepNumber === currentStep) return 'active';
    return 'pending';
  };

  return (
    <div className="w-full max-w-xl mx-auto p-6 bg-white rounded-2xl border">
      <div className="space-y-6">
        {steps.map((step, index) => {
          const state = getStepState(step.number);
          const isLast = index === steps.length - 1;

          return (
            <div key={step.number} className="relative">
              <div className="flex items-start gap-4">
                {/* Step Indicator */}
                <div className="flex-shrink-0">
                  <div
                    className={cn(
                      'w-10 h-10 rounded-full flex items-center justify-center transition-all',
                      state === 'completed' && 'bg-success text-white',
                      state === 'active' && 'bg-primary text-white animate-pulse-slow',
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

                {/* Step Content */}
                <div className="flex-1 pb-6">
                  <h4
                    className={cn(
                      'font-medium',
                      state === 'pending' ? 'text-gray-400' : 'text-foreground'
                    )}
                  >
                    {step.title}
                  </h4>
                  <p
                    className={cn(
                      'text-sm mt-1',
                      state === 'pending'
                        ? 'text-gray-300'
                        : 'text-muted-foreground'
                    )}
                  >
                    {step.description}
                  </p>

                  {/* Progress Bar */}
                  {state === 'active' && (
                    <div className="mt-3">
                      <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-primary rounded-full transition-all duration-500"
                          style={{ width: `${step.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Connector Line */}
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
    </div>
  );
}


