/**
 * LabelCheck UA — API client
 *
 * Тонкий шар над fetch:
 *   - формує URL з NEXT_PUBLIC_API_URL (який вже містить /api)
 *   - підтримує AbortController для скасування
 *   - кидає типізовані помилки (APIError / NetworkError / AbortedError)
 *   - використовує канонічні типи з ./types (контракт з бекендом 1:1)
 *
 * Усі контракти типів живуть у ./types. Імпортуй потрібні типи звідти —
 * цей файл повторно нічого не реекспортує (раніше тут був legacy-shim,
 * прибраний у Priority 4 cleanup).
 */

import type {
  APIErrorResponse,
  FullCheckResponse,
  QuickCheckResponse,
} from './types';

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
 * Endpoint-шлях додаємо напряму: `${base}/check-label/quick`.
 * Якщо env задана без /api — fetch отримає 404, UI покаже помилку
 * `api_url_missing` через checker-errors.ts.
 */
const base = (API_BASE_URL ?? 'http://localhost:8000/api').replace(/\/+$/, '');

// ==========================================
// ERRORS
// ==========================================

/**
 * Помилка API. Містить HTTP-статус та повідомлення з бекенду (detail).
 * Використовуй `err.status` у UI щоб розрізняти 404 / 500 / тощо.
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
 * Це НЕ помилка в сенсі UI — не показувати алерт, просто тихо повернути в idle.
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
  return apiFetch<FullCheckResponse>('/check-label/full', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ check_id: checkId }),
    signal,
  });
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
 * @param options.signal  AbortSignal для скасування (спільний для обох запитів)
 * @param options.onQuickDone  колбек після Quick — дає UI можливість оновити
 *                             прогрес та показати інгредієнти, поки чекаємо Full
 * @returns               результат Full-перевірки
 */
export async function checkLabel(
  file: File,
  options?: {
    signal?: AbortSignal;
    onQuickDone?: (quick: QuickCheckResponse) => void;
  },
): Promise<FullCheckResponse> {
  const { signal, onQuickDone } = options ?? {};
  const quick = await quickCheck(file, signal);
  onQuickDone?.(quick);
  return fullCheck(quick.check_id, signal);
}
