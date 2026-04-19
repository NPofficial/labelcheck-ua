/**
 * LabelCheck UA — API client
 *
 * Тонкий шар над fetch, який:
 *   - формує правильний URL з NEXT_PUBLIC_API_URL (який вже містить /api)
 *   - підтримує AbortController для скасування
 *   - кидає типізовані помилки (APIError)
 *   - використовує точні типи з lib/types.ts (контракт з бекендом)
 *
 * НЕ використовувати типи з цього файлу для UI —
 * беріть їх з lib/types.ts. Тут тільки API-рівень.
 */

import type {
  QuickCheckResponse,
  FullCheckResponse as _CanonicalFullCheckResponse,
  DosageError as _CanonicalDosageError,
  DosageWarning as _CanonicalDosageWarning,
  APIErrorResponse,
} from './types';

/**
 * @deprecated Ширший legacy-тип, який старий UI (ResultsReport, ErrorCard,
 * WarningCard) споживає через `@/lib/api-client`.
 *
 * Для нового коду бери канонічний `FullCheckResponse` з `./types`.
 *
 * Розширення:
 *   - errors/warnings отримують плоскі поля `field` та `penalty` (маппінг зі
 *     старого UI; backend їх не повертає, але фронт-код на них посилається).
 *   - додаються `mandatory_fields` / `forbidden_phrases` (групування, якого
 *     немає в канонічній формі — вони лежать у `compliance_errors`).
 *   - `penalties.total` як аліас для `penalties.total_amount`.
 */
type FullCheckResponse = Omit<
  _CanonicalFullCheckResponse,
  'errors' | 'warnings' | 'penalties'
> & {
  errors: Array<_CanonicalDosageError & { field: string; penalty: number }>;
  warnings: Array<
    _CanonicalDosageWarning & {
      field: string;
      penalty: number;
      /** Narrowed for legacy UI — DosageWarning.source canonical is string|null. */
      source: string;
    }
  >;
  penalties: _CanonicalFullCheckResponse['penalties'] & {
    /** @deprecated Використовуй `total_amount`. */
    total?: number;
  };
  /** @deprecated Legacy-групування. Використовуй `compliance_errors`. */
  mandatory_fields?: {
    present?: string[];
    missing?: string[];
  };
  /** @deprecated Legacy-групування. Використовуй `compliance_errors`. */
  forbidden_phrases?: {
    found?: string[];
    allowed?: string[];
  };
};

// ==========================================
// CONFIG
// ==========================================

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_BASE_URL && typeof window !== 'undefined') {
  console.error(
    '[api-client] NEXT_PUBLIC_API_URL is not set. ' +
      'Add it to .env.local (dev) or Netlify Environment Variables (prod). ' +
      'Expected format: https://labelcheck-api.up.railway.app/api',
  );
}

/**
 * URL має закінчуватися на /api (див. .env.local.example).
 * Ми додаємо endpoint-шлях напряму: `${base}/check-label/quick`.
 * Якщо env задана без /api — fetch кине 404, UI покаже api_url_missing-помилку.
 */
const base = (API_BASE_URL ?? 'http://localhost:8000/api').replace(/\/+$/, '');

// ==========================================
// ERRORS
// ==========================================

/**
 * Помилка API. Містить HTTP статус та повідомлення з бекенду (detail).
 * Використовуй `err.status` у UI щоб розрізняти сценарії (404 / 500 / network).
 */
export class APIError extends Error {
  readonly status: number;
  readonly endpoint: string;

  constructor(params: { status: number; endpoint: string; message: string }) {
    super(params.message);
    this.name = 'APIError';
    this.status = params.status;
    this.endpoint = params.endpoint;
  }
}

/**
 * Мережева помилка (fetch кинув TypeError) — окремо від APIError,
 * щоб UI показував різні повідомлення.
 */
export class NetworkError extends Error {
  readonly endpoint: string;

  constructor(params: { endpoint: string; cause?: unknown }) {
    super('Network request failed');
    this.name = 'NetworkError';
    this.endpoint = params.endpoint;
    if (params.cause !== undefined) {
      (this as { cause?: unknown }).cause = params.cause;
    }
  }
}

/**
 * Скасовано користувачем (AbortController.abort()).
 * Це НЕ помилка в сенсі UI — не показувати алерт, просто тихо повернути в стан idle.
 */
export class AbortedError extends Error {
  constructor() {
    super('Request aborted by user');
    this.name = 'AbortedError';
  }
}

// ==========================================
// INTERNAL FETCH WRAPPER
// ==========================================

async function apiFetch<T>(
  endpoint: string,
  init: RequestInit & { signal?: AbortSignal },
): Promise<T> {
  const url = `${base}${endpoint}`;

  let response: Response;
  try {
    response = await fetch(url, init);
  } catch (err) {
    // fetch() кидає TypeError на мережеві проблеми І на AbortError.
    // Розрізняємо за signal.aborted.
    if (init.signal?.aborted) {
      throw new AbortedError();
    }
    throw new NetworkError({ endpoint, cause: err });
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = (await response.json()) as APIErrorResponse;
      if (body.detail) detail = body.detail;
    } catch {
      // Body не JSON або порожнє — лишаємо fallback "HTTP XXX".
    }
    throw new APIError({ status: response.status, endpoint, message: detail });
  }

  return (await response.json()) as T;
}

// ==========================================
// PUBLIC API
// ==========================================

/**
 * POST /api/check-label/quick
 *
 * Етап 1: OCR через Claude Vision. Витягує інгредієнти та метадані з етикетки.
 * Очікуваний час: 30–40 секунд.
 */
export async function quickCheck(
  file: File,
  signal?: AbortSignal,
): Promise<QuickCheckResponse> {
  const formData = new FormData();
  formData.append('file', file);

  return apiFetch<QuickCheckResponse>('/check-label/quick', {
    method: 'POST',
    body: formData,
    signal,
  });
}

/**
 * POST /api/check-label/full
 * Body: { check_id }
 *
 * Етап 2: повна валідація (dosage + compliance).
 * Очікуваний час: 10–20 секунд.
 */
export async function fullCheck(
  checkId: string,
  signal?: AbortSignal,
): Promise<FullCheckResponse> {
  const raw = await apiFetch<_CanonicalFullCheckResponse>('/check-label/full', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ check_id: checkId }),
    signal,
  });
  return raw as unknown as FullCheckResponse;
}

/**
 * URL для PDF-звіту. Відкривати через window.open() або <a download>.
 * Цей метод НЕ робить fetch — тільки формує URL.
 */
export function getReportUrl(checkId: string): string {
  return `${base}/check-label/${checkId}/report.pdf`;
}

/**
 * Повний flow: Quick → Full. Використовувати в UI замість ручного ланцюжка.
 *
 * @param file            файл від користувача
 * @param signal          AbortSignal для скасування (спільний для обох запитів)
 * @param onQuickDone     колбек після Quick (щоб UI оновив прогрес та показав інгредієнти)
 * @returns               результат Full-перевірки
 */
export async function checkLabel(
  file: File,
  options?: {
    signal?: AbortSignal;
    onQuickDone?: (quick: QuickCheckResponse) => void;
  },
): Promise<FullCheckResponse>;
/**
 * @deprecated Legacy callback-сигнатура старого UI.
 * Використовуй об'єктний варіант з `onQuickDone`.
 *
 * Колбек викликається з (step, progress):
 *   step=1, progress=100 — коли Quick готовий
 *   step=2, progress=0   — старт Full
 *   step=2, progress=100 — Full готовий
 */
export async function checkLabel(
  file: File,
  onProgress: (step: 1 | 2, progress: number) => void,
): Promise<FullCheckResponse>;
export async function checkLabel(
  file: File,
  arg?:
    | ((step: 1 | 2, progress: number) => void)
    | {
        signal?: AbortSignal;
        onQuickDone?: (quick: QuickCheckResponse) => void;
      },
): Promise<FullCheckResponse> {
  if (typeof arg === 'function') {
    const onProgress = arg;
    const quick = await quickCheck(file);
    onProgress(1, 100);
    onProgress(2, 0);
    const full = await fullCheck(quick.check_id);
    onProgress(2, 100);
    return full;
  }
  const options = arg ?? {};
  const quick = await quickCheck(file, options.signal);
  options.onQuickDone?.(quick);
  const full = await fullCheck(quick.check_id, options.signal);
  return full;
}

// ==========================================
// BACKWARD COMPATIBILITY (legacy exports)
// ==========================================
//
// Ці експорти існують лише щоб старий код (checker/page.tsx, UploadZone.tsx,
// ResultsReport.tsx) компілювався без змін. Для нового коду бери типи напряму
// з './types', а PDF відкривай через getReportUrl().
//

export type {
  QuickCheckResponse,
  DosageError,
  DosageWarning,
  ComplianceError,
  ParsedIngredient,
} from './types';

export type { FullCheckResponse };

/**
 * @deprecated Використовуй точні типи з `./types`
 * ({@link DosageError}, {@link DosageWarning}, {@link ComplianceError}).
 * Цей тип — спільний legacy-інтерфейс старого UI.
 */
export type ValidationError = {
  field?: string;
  message: string;
  source?: string;
  penalty?: number;
  recommendation?: string;
  level?: 'error' | 'warning';
};

/**
 * @deprecated Використовуй {@link ParsedIngredient} (Full) або
 * `QuickIngredient` (Quick) з `./types`.
 */
export type Ingredient = {
  name: string;
  quantity: number | null;
  unit: string;
  form?: string | null;
};

/**
 * @deprecated Використовуй `FullCheckResponse['product_info']` або
 * `QuickCheckResponse['product_info']` з `./types`.
 */
export type ProductInfo = {
  name: string | null;
  form?: string | null;
  quantity?: number | null;
  ingredients: Array<{
    name: string;
    quantity: number | null;
    unit: string;
    form?: string | null;
  }>;
};

/**
 * @deprecated Замість завантаження через fetch+Blob — формуй URL через
 * {@link getReportUrl} та відкривай через `window.open(url)` або
 * `<a href={url} download>`. Браузер сам обробить PDF.
 *
 * Ця обгортка залишена лише для legacy-коду, який явно працює з Blob.
 */
export async function downloadReport(
  checkId: string,
  signal?: AbortSignal,
): Promise<Blob> {
  const endpoint = `/check-label/${checkId}/report.pdf`;
  const url = `${base}${endpoint}`;

  let response: Response;
  try {
    response = await fetch(url, { method: 'GET', signal });
  } catch (err) {
    if (signal?.aborted) {
      throw new AbortedError();
    }
    throw new NetworkError({ endpoint, cause: err });
  }

  if (!response.ok) {
    let detail = `HTTP ${response.status}`;
    try {
      const body = (await response.json()) as APIErrorResponse;
      if (body.detail) detail = body.detail;
    } catch {
      // Body не JSON або порожнє — лишаємо fallback.
    }
    throw new APIError({ status: response.status, endpoint, message: detail });
  }

  return response.blob();
}
