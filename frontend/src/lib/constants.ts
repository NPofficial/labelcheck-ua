// src/lib/constants.ts

export const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export const ACCEPTED_FILE_TYPES = {
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'application/pdf': ['.pdf'],
};

export const ACCEPTED_FILE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.pdf'];

export const API_ENDPOINTS = {
  quickCheck: '/api/check-label/quick',
  fullCheck: '/api/check-label/full',
  report: (checkId: string) => `/api/check-label/${checkId}/report.pdf`,
} as const;

export const PENALTY_AMOUNTS = {
  critical: 640000,
  high: 125200,
  medium: 62600,
} as const;

export const BREAKPOINTS = {
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
} as const;

export const NAV_LINKS = [
  { href: '/#how-it-works', label: 'Як це працює' },
  { href: '/pricing', label: 'Тарифи' },
  { href: '/checker', label: 'Перевірка' },
  { href: '/generator', label: 'Генератор', badge: 'Скоро' },
] as const;


