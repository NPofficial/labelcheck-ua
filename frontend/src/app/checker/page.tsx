'use client';

import { useState, useCallback } from 'react';
import { content } from '@/content/ua';
import { checkLabel, downloadReport, type FullCheckResponse } from '@/lib/api-client';
import { UploadZone, ProgressStepper, ResultsReport } from '@/components/checker';

type CheckerState = 'idle' | 'uploading' | 'analyzing' | 'complete' | 'error';

export default function CheckerPage() {
  const [state, setState] = useState<CheckerState>('idle');
  const [currentStep, setCurrentStep] = useState<1 | 2>(1);
  const [step1Progress, setStep1Progress] = useState(0);
  const [step2Progress, setStep2Progress] = useState(0);
  const [result, setResult] = useState<FullCheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [checkId, setCheckId] = useState<string | null>(null);

  const handleFileSelect = useCallback(async (file: File) => {
    setState('uploading');
    setError(null);
    setCurrentStep(1);
    setStep1Progress(0);
    setStep2Progress(0);

    // Simulate progress for better UX
    const progressInterval = setInterval(() => {
      setStep1Progress((prev) => {
        if (prev >= 90) return prev;
        return prev + 10;
      });
    }, 200);

    try {
      const fullResult = await checkLabel(file, (step, progress) => {
        if (step === 1) {
          clearInterval(progressInterval);
          setStep1Progress(progress);
          if (progress === 100) {
            setCurrentStep(2);
            setState('analyzing');
          }
        } else {
          setStep2Progress(progress);
        }
      });

      clearInterval(progressInterval);
      setResult(fullResult);
      setCheckId(fullResult.check_id);
      setState('complete');
    } catch (err) {
      clearInterval(progressInterval);
      setError(err instanceof Error ? err.message : content.checker.errors.analysisFailed);
      setState('error');
    }
  }, []);

  const handleDownloadPdf = useCallback(async () => {
    if (!checkId) return;
    
    try {
      const blob = await downloadReport(checkId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `label-check-report-${checkId}.pdf`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download PDF:', err);
    }
  }, [checkId]);

  const handleSendEmail = useCallback(() => {
    // TODO: Implement email sending
    console.log('Send email');
  }, []);

  const handleShare = useCallback(async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title: 'LabelCheck UA - Результати перевірки',
          text: `Перевірка етикетки завершена. ${result?.is_valid ? 'Етикетка відповідає вимогам.' : `Виявлено ${result?.errors.length} помилок.`}`,
          url: window.location.href,
        });
      } catch (err) {
        console.error('Share failed:', err);
      }
    }
  }, [result]);

  const handleCheckAnother = useCallback(() => {
    setState('idle');
    setResult(null);
    setCheckId(null);
    setError(null);
    setCurrentStep(1);
    setStep1Progress(0);
    setStep2Progress(0);
  }, []);

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gradient-hero">
      <div className="container mx-auto px-4 py-8 md:py-12">
        {/* Header */}
        <div className="text-center mb-8 md:mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3">
            {content.checker.title}
          </h1>
          <p className="text-lg text-muted-foreground">
            {content.checker.subtitle}
          </p>
        </div>

        {/* Content based on state */}
        {state === 'idle' && (
          <UploadZone
            onFileSelect={handleFileSelect}
            isLoading={false}
            error={error || undefined}
          />
        )}

        {(state === 'uploading' || state === 'analyzing') && (
          <ProgressStepper
            currentStep={currentStep}
            step1Progress={step1Progress}
            step2Progress={step2Progress}
          />
        )}

        {state === 'complete' && result && (
          <ResultsReport
            result={result}
            onDownloadPdf={handleDownloadPdf}
            onSendEmail={handleSendEmail}
            onShare={handleShare}
            onCheckAnother={handleCheckAnother}
          />
        )}

        {state === 'error' && (
          <div className="max-w-xl mx-auto">
            <div className="bg-white rounded-2xl border p-6 text-center">
              <div className="w-16 h-16 rounded-full bg-error-light flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">😕</span>
              </div>
              <h3 className="text-xl font-semibold text-foreground mb-2">
                {content.common.error}
              </h3>
              <p className="text-muted-foreground mb-6">
                {error || content.checker.errors.analysisFailed}
              </p>
              <button
                onClick={handleCheckAnother}
                className="px-6 py-2 bg-primary text-white rounded-lg hover:bg-primary/90 transition-colors"
              >
                Спробувати ще раз
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


