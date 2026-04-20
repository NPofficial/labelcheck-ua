/**
 * Маппінг помилок API + валідації на CheckerErrorReason
 * та локалізовані повідомлення для UI.
 */

import { APIError, NetworkError } from './api-client';
import type { CheckerErrorReason } from './types';

export interface ErrorPresentation {
  /** Заголовок (короткий, що пішло не так). */
  title: string;
  /** Опис (детально, що робити). */
  description: string;
  /** Текст основної кнопки відновлення. */
  primaryAction: string;
  /** Чи є сенс пробувати знову з тим самим файлом. */
  canRetrySameFile: boolean;
  /** Чи показувати кнопку "Вибрати інший файл". */
  canPickNewFile: boolean;
}

/**
 * Класифікація помилки, що сталася на етапі Quick або Full.
 */
export function mapApiErrorToReason(
  err: unknown,
  stage: 'quick' | 'full'
): CheckerErrorReason {
  if (err instanceof NetworkError) {
    return 'network_error';
  }

  if (err instanceof APIError) {
    // Full-сесія не знайдена → бек повертає 404 на /check-label/full
    if (stage === 'full' && err.status === 404) {
      return 'full_session_not_found';
    }

    // Таймаути на Quick (бек повертає 408 або 504; може бути і 500 з "timeout" в detail)
    if (stage === 'quick') {
      if (err.status === 408 || err.status === 504) return 'quick_timeout';
      if (err.message.toLowerCase().includes('timeout')) return 'quick_timeout';
      return 'quick_failed';
    }

    return 'full_failed';
  }

  // Невідома помилка — трактуємо як збій етапу
  return stage === 'quick' ? 'quick_failed' : 'full_failed';
}

/**
 * Перевірка налаштувань — чи задано NEXT_PUBLIC_API_URL.
 * Викликати один раз на маунті сторінки.
 */
export function isApiUrlMissing(): boolean {
  if (typeof window === 'undefined') return false;
  return !process.env.NEXT_PUBLIC_API_URL;
}

/**
 * Локалізовані повідомлення для всіх 9 reason'ів.
 */
const PRESENTATIONS: Record<CheckerErrorReason, ErrorPresentation> = {
  file_too_large: {
    title: 'Файл занадто великий',
    description: 'Максимальний розмір файлу — 10 МБ. Спробуйте стиснути зображення або зробити нову фотографію з меншою якістю.',
    primaryAction: 'Вибрати інший файл',
    canRetrySameFile: false,
    canPickNewFile: true,
  },
  invalid_format: {
    title: 'Невірний формат файлу',
    description: 'Підтримуються лише JPG, PNG та PDF. Конвертуйте файл у дозволений формат і спробуйте ще раз.',
    primaryAction: 'Вибрати інший файл',
    canRetrySameFile: false,
    canPickNewFile: true,
  },
  quick_failed: {
    title: 'Не вдалося розпізнати етикетку',
    description: 'Сервіс OCR повернув помилку. Можливо, зображення нечітке або погано освітлене. Спробуйте інше фото.',
    primaryAction: 'Спробувати ще раз',
    canRetrySameFile: true,
    canPickNewFile: true,
  },
  quick_timeout: {
    title: 'Час очікування вичерпано',
    description: 'Розпізнавання тексту зайняло більше 60 секунд. Перевірте швидкість інтернету та спробуйте ще раз.',
    primaryAction: 'Спробувати ще раз',
    canRetrySameFile: true,
    canPickNewFile: true,
  },
  full_session_not_found: {
    title: 'Сесію перевірки втрачено',
    description: 'Перший етап завершився, але сервер не знайшов даних для другого. Це могло статися через перезапуск сервісу. Завантажте файл повторно.',
    primaryAction: 'Почати спочатку',
    canRetrySameFile: true,
    canPickNewFile: true,
  },
  full_failed: {
    title: 'Помилка під час перевірки',
    description: 'Текст розпізнано, але валідація відповідності не завершилась. Спробуйте ще раз — це часто допомагає.',
    primaryAction: 'Спробувати ще раз',
    canRetrySameFile: true,
    canPickNewFile: true,
  },
  network_error: {
    title: 'Немає зв\'язку з сервером',
    description: 'Не вдалося надіслати запит. Перевірте інтернет-з\'єднання та спробуйте ще раз.',
    primaryAction: 'Спробувати ще раз',
    canRetrySameFile: true,
    canPickNewFile: true,
  },
  api_url_missing: {
    title: 'Сервіс не налаштований',
    description: 'Адреса API не задана в конфігурації. Зверніться до адміністратора (NEXT_PUBLIC_API_URL).',
    primaryAction: 'Оновити сторінку',
    canRetrySameFile: false,
    canPickNewFile: false,
  },
};

export function getErrorPresentation(reason: CheckerErrorReason): ErrorPresentation {
  return PRESENTATIONS[reason];
}
