// Re-export API types
export type {
  Ingredient,
  ProductInfo,
  QuickCheckResponse,
  ValidationError,
  FullCheckResponse,
} from '@/lib/api-client';

// Checker state types
export type CheckerState = 'idle' | 'uploading' | 'analyzing' | 'complete' | 'error';

// UI types
export interface NavLink {
  href: string;
  label: string;
  badge?: string;
}

export interface FooterLink {
  label: string;
  href: string;
}

export interface Plan {
  name: string;
  price: string;
  period: string;
  description: string;
  features: string[];
  cta: string;
  popular: boolean;
}


