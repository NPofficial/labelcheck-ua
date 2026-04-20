'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { AlertCircle, RefreshCw, Upload as UploadIcon } from 'lucide-react';
import { content } from '@/content/ua';
import {
  checkLabel,
  getReportUrl,
  AbortedError,
} from '@/lib/api-client';
import {
  mapApiErrorToReason,
  isApiUrlMissing,
  getErrorPresentation,
} from '@/lib/checker-errors';
import type {
  CheckerState,
  CheckerErrorReason,
  FullCheckResponse,
  QuickCheckResponse,
} from '@/lib/types';
import { UploadZone, ProgressStepper, ResultsReport } from '@/components/checker';
import { Button } from '@/components/ui/button';

export default function CheckerPage() {
  const [state, setState] = useState<CheckerState>({ kind: 'idle' });

  // Тримаємо посилання на поточний AbortController, щоб обробник Esc міг
  // дістатися до нього без замикання state.
  const activeAbortRef = useRef<AbortController | null>(null);

  // Esc → скасувати активне завантаження
  useEffect(() => {
    if (state.kind !== 'quick_loading' && state.kind !== 'full_loading') return;

    const handler = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        activeAbortRef.current?.abort();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [state.kind]);

  // ============================================================
  // FLOW: idle → quick_loading → full_loading → success | error
  // ============================================================

  const startCheck = useCallback(async (file: File) => {
    if (isApiUrlMissing()) {
      setState({ kind: 'error', reason: 'api_url_missing', retryPayload: { file } });
      return;
    }

    const abort = new AbortController();
    activeAbortRef.current = abort;

    setState({
      kind: 'quick_loading',
      file,
      previewUrl: null,
      abort,
    });

    let stage: 'quick' | 'full' = 'quick';

    try {
      const fullResult: FullCheckResponse = await checkLabel(file, {
        signal: abort.signal,
        onQuickDone: (quick: QuickCheckResponse) => {
          stage = 'full';
          setState({
            kind: 'full_loading',
            file,
            previewUrl: null,
            quick,
            abort,
          });
        },
      });

      activeAbortRef.current = null;
      setState({
        kind: 'success',
        result: fullResult,
        file,
        previewUrl: null,
      });
    } catch (err) {
      activeAbortRef.current = null;

      // Тиха обробка скасування — просто повертаємось у idle
      if (err instanceof AbortedError || (err instanceof DOMException && err.name === 'AbortError')) {
        setState({ kind: 'idle' });
        return;
      }

      const reason = mapApiErrorToReason(err, stage);
      setState({
        kind: 'error',
        reason,
        retryPayload: { file },
      });
    }
  }, []);

  const handleCancel = useCallback(() => {
    activeAbortRef.current?.abort();
  }, []);

  const handleCheckAnother = useCallback(() => {
    activeAbortRef.current?.abort();
    activeAbortRef.current = null;
    setState({ kind: 'idle' });
  }, []);

  const handleRetry = useCallback(() => {
    if (state.kind !== 'error' || !state.retryPayload?.file) {
      setState({ kind: 'idle' });
      return;
    }
    void startCheck(state.retryPayload.file);
  }, [state, startCheck]);

  const handleDownloadPdf = useCallback(() => {
    if (state.kind !== 'success') return;
    const url = getReportUrl(state.result.check_id);
    window.open(url, '_blank', 'noopener,noreferrer');
  }, [state]);

  const handleSendEmail = useCallback(() => {
    // TODO (Етап 5): реалізувати надсилання звіту на email
    console.warn('Email sending not implemented yet');
  }, []);

  const handleShare = useCallback(async () => {
    if (state.kind !== 'success') return;
    if (!navigator.share) return;

    try {
      await navigator.share({
        title: 'LabelCheck UA — Результати перевірки',
        text: state.result.is_valid
          ? 'Етикетка відповідає вимогам.'
          : `Виявлено ${state.result.errors.length} критичних помилок.`,
        url: window.location.href,
      });
    } catch {
      // Скасування через системний UI — ігноруємо
    }
  }, [state]);

  // ============================================================
  // RENDER
  // ============================================================

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gradient-hero">
      <div className="container mx-auto px-4 py-8 md:py-12">
        <div className="text-center mb-8 md:mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-3">
            {content.checker.title}
          </h1>
          <p className="text-lg text-muted-foreground">{content.checker.subtitle}</p>
        </div>

        {state.kind === 'idle' && <UploadZone onFileSelect={startCheck} />}

        {(state.kind === 'quick_loading' || state.kind === 'full_loading') && (
          <ProgressStepper
            currentStep={state.kind === 'quick_loading' ? 1 : 2}
            fileName={state.file.name}
            onCancel={handleCancel}
          />
        )}

        {state.kind === 'success' && (
          <ResultsReport
            result={state.result}
            onDownloadPdf={handleDownloadPdf}
            onSendEmail={handleSendEmail}
            onShare={handleShare}
            onCheckAnother={handleCheckAnother}
          />
        )}

        {state.kind === 'error' && (
          <ErrorScreen
            reason={state.reason}
            onRetry={handleRetry}
            onPickNewFile={handleCheckAnother}
          />
        )}
      </div>
    </div>
  );
}

// ============================================================
// ERROR SCREEN
// ============================================================

interface ErrorScreenProps {
  reason: CheckerErrorReason;
  onRetry: () => void;
  onPickNewFile: () => void;
}

function ErrorScreen({ reason, onRetry, onPickNewFile }: ErrorScreenProps) {
  const presentation = getErrorPresentation(reason);

  const handlePrimary = () => {
    if (reason === 'api_url_missing') {
      window.location.reload();
      return;
    }
    if (presentation.canRetrySameFile) {
      onRetry();
    } else {
      onPickNewFile();
    }
  };

  return (
    <div className="max-w-xl mx-auto">
      <div className="bg-white rounded-2xl border p-6">
        <div className="w-16 h-16 rounded-full bg-error-light flex items-center justify-center mx-auto mb-4">
          <AlertCircle className="h-8 w-8 text-error" />
        </div>
        <h3 className="text-xl font-semibold text-foreground text-center mb-2">
          {presentation.title}
        </h3>
        <p className="text-muted-foreground text-center mb-6">{presentation.description}</p>

        <div className="flex flex-col sm:flex-row gap-3">
          <Button
            onClick={handlePrimary}
            className="flex-1 bg-gradient-primary hover:opacity-90 text-white"
          >
            {presentation.canRetrySameFile && reason !== 'api_url_missing' ? (
              <RefreshCw className="mr-2 h-4 w-4" />
            ) : (
              <UploadIcon className="mr-2 h-4 w-4" />
            )}
            {presentation.primaryAction}
          </Button>

          {presentation.canPickNewFile && presentation.canRetrySameFile && (
            <Button onClick={onPickNewFile} variant="outline" className="flex-1">
              <UploadIcon className="mr-2 h-4 w-4" />
              Вибрати інший файл
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
