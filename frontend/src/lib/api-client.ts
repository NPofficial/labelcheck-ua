// src/lib/api-client.ts

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface Ingredient {
  name: string;
  quantity: number;
  unit: string;
  form?: string;
}

export interface ProductInfo {
  name: string;
  form?: string;
  quantity?: number;
  ingredients: Ingredient[];
}

export interface QuickCheckResponse {
  check_id: string;
  product_info: ProductInfo;
  extracted_text: string;
}

export interface ValidationError {
  field: string;
  message: string;
  source: string;
  penalty: number;
  recommendation?: string;
  level: 'error' | 'warning';
}

export interface FullCheckResponse {
  check_id: string;
  is_valid: boolean;
  product_info: ProductInfo;
  errors: ValidationError[];
  warnings: ValidationError[];
  mandatory_fields: {
    present: string[];
    missing: string[];
  };
  forbidden_phrases: {
    found: string[];
  };
  penalties: {
    total: number;
    breakdown: Array<{
      source: string;
      amount: number;
    }>;
  };
}

// API Functions
export async function quickCheck(file: File): Promise<QuickCheckResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE_URL}/api/check-label/quick`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || error.detail || 'Quick check failed');
  }

  return response.json();
}

export async function fullCheck(checkId: string): Promise<FullCheckResponse> {
  const response = await fetch(`${API_BASE_URL}/api/check-label/full`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ check_id: checkId }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || error.detail || 'Full check failed');
  }

  return response.json();
}

export async function downloadReport(checkId: string): Promise<Blob> {
  const response = await fetch(`${API_BASE_URL}/api/check-label/${checkId}/report.pdf`);

  if (!response.ok) {
    throw new Error('Failed to download report');
  }

  return response.blob();
}

// Helper function for full flow
export async function checkLabel(
  file: File, 
  onProgress?: (step: number, progress: number) => void
): Promise<FullCheckResponse> {
  // Step 1: Quick check (OCR)
  onProgress?.(1, 0);
  const quickResult = await quickCheck(file);
  onProgress?.(1, 100);

  // Step 2: Full check (Validation)
  onProgress?.(2, 0);
  const fullResult = await fullCheck(quickResult.check_id);
  onProgress?.(2, 100);

  return fullResult;
}


