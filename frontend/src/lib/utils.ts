// src/lib/utils.ts

import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('uk-UA', {
    style: 'decimal',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount) + ' грн';
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function validateFile(file: File): { valid: boolean; error?: string } {
  const MAX_SIZE = 10 * 1024 * 1024; // 10MB
  const VALID_TYPES = ['image/jpeg', 'image/png', 'application/pdf'];

  if (!VALID_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: 'Невірний формат файлу. Підтримуються: JPG, PNG, PDF',
    };
  }

  if (file.size > MAX_SIZE) {
    return {
      valid: false,
      error: 'Файл занадто великий. Максимальний розмір: 10 МБ',
    };
  }

  return { valid: true };
}

export function getErrorSeverityColor(level: 'error' | 'warning' | 'success'): string {
  const colors = {
    error: 'text-red-600 bg-red-50 border-red-200',
    warning: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    success: 'text-green-600 bg-green-50 border-green-200',
  };
  return colors[level];
}

export function getFileType(file: File): 'image' | 'pdf' | 'other' {
  if (file.type === 'image/jpeg' || file.type === 'image/png') {
    return 'image';
  }
  if (file.type === 'application/pdf') {
    return 'pdf';
  }
  return 'other';
}

export function isImageFile(file: File): boolean {
  return file.type === 'image/jpeg' || file.type === 'image/png';
}

export function isPdfFile(file: File): boolean {
  return file.type === 'application/pdf';
}
