/**
 * LabelCheck UA — TypeScript типи для API
 *
 * 🔒 ЦЕЙ ФАЙЛ ВІДПОВІДАЄ PYDANTIC-МОДЕЛЯМ БЕКЕНДУ 1:1.
 * Не редагуй без синхронізації з:
 *   backend/app/api/schemas/validation.py
 *   backend/app/api/schemas/compliance.py
 *   backend/app/api/routes/checker.py (response shape)
 *
 * Якщо щось не збігається — це баг (фронта чи бека), не мовчки виправляй.
 */

// ==========================================
// DOSAGE (перевірка доз інгредієнтів)
// ==========================================

/**
 * Рівні ієрархії перевірки доз:
 *   0 — заборонена речовина (banned_substances)
 *   1 — EFSA Upper Limit (UL)
 *   2 — EFSA Safe Level
 *   3 — Таблиця 1 / amino_acids / allowed_plants / microorganisms
 *   4 — Додаток 3 (physiological, novel_foods, other_substances)
 */
export type DosageErrorLevel = 0 | 1 | 2 | 3 | 4;

/**
 * Джерело перевірки — звідки взято ліміт.
 * Значення згенеровані бекендом, тому тип відкритий (string).
 * Відомі значення: efsa_ul, efsa_safe, table1, amino_acids_table,
 * allowed_plants, microorganisms, physiological_table, novel_foods,
 * other_substances, banned_substances, no_limit_available, unknown.
 */
export type DosageSource = string;

export interface DosageError {
  ingredient: string;
  message: string;
  level: DosageErrorLevel;
  source: DosageSource;
  current_dose: string | null;
  max_allowed: string | null;
  three_times_limit: string | null;
  current_form: string | null;
  allowed_forms: string[] | null;
  regulatory_source: string;
  recommendation: string;
  penalty_amount: number; // UAH
}

export interface DosageWarning {
  ingredient: string;
  message: string;
  /** null означає "інформаційне повідомлення", не рівень помилки. */
  level: DosageErrorLevel | null;
  source: DosageSource | null;
  current_dose: string | null;
  max_allowed: string | null;
  recommendation: string;
}

// ==========================================
// COMPLIANCE (заборонені фрази + обов'язкові поля)
// ==========================================

export type ComplianceErrorType = 'forbidden_phrase' | 'mandatory_field';

export interface ComplianceError {
  type: ComplianceErrorType;
  /** Заповнено для type === 'mandatory_field'. */
  field_name: string | null;
  /** Заповнено для type === 'forbidden_phrase'. */
  phrase: string | null;
  /** Заповнено для type === 'forbidden_phrase'. */
  category: string | null;
  regulatory_source: string;
  article_number: string | null;
  error_message: string;
  explanation: string | null;
  /** 'critical' | 'high' | 'medium' — тільки для forbidden_phrase. */
  severity: string | null;
  recommendation: string;
  penalty_amount: number; // UAH
}

// ==========================================
// PRODUCT / INGREDIENTS
// ==========================================

export type ProductForm = 'tablets' | 'capsules' | 'powder' | 'liquid';

/**
 * Інгредієнт у Quick-відповіді (плаский, мало полів).
 */
export interface QuickIngredient {
  name: string;
  quantity: number | null;
  unit: string;
  form: string | null;
  type: 'active' | 'excipient' | null;
}

/**
 * Інгредієнт у Full-відповіді (обогачений через SubstanceMapperService).
 * Поле `found` — чи знайдено речовину в БД хоч якимось способом.
 */
export interface ParsedIngredient {
  name: string;
  quantity: number | null;
  unit: string;

  /** 'active' | 'excipient' | 'plant' | null — після мапінгу може змінитися. */
  type: string | null;

  /** Форма речовини (напр. "Цитрат", "Піридоксину гідрохлорид"). */
  form: string | null;

  /** true якщо речовину розпізнано в БД (навіть як plant або excipient). */
  found: boolean;

  /** Базова речовина (напр. "Магній" замість "цитрат магнію"). */
  base_substance: string | null;

  /** 'excipients_db' | 'allowed_plants' | null. */
  source: string | null;

  /** Елементарна кількість (напр. 100 мг Mg з 500 мг цитрату магнію). */
  elemental_quantity: number | null;

  /** Коефіцієнт конверсії (напр. 0.2 для цитрату магнію). */
  coefficient_used: number | null;

  is_extract: boolean;

  /** Тип екстракту (якщо is_extract): "екстракт", "порошок", "олія"... */
  extract_type: string | null;

  /** "10:1", "20:1" якщо розпізнано. */
  ratio: string | null;

  /** Якщо інгредієнт був частиною композиції — оригінальна назва. */
  _from_composition?: string;
}

// ==========================================
// LABEL METADATA
// ==========================================

export interface Operator {
  name: string | null;
  edrpou: string | null;
  address: string | null;
  phone?: string | null;
}

export interface Manufacturer {
  name: string | null;
  address: string | null;
}

export interface MandatoryPhrases {
  has_dietary_supplement_label: boolean;
  has_not_medicine: boolean;
  has_not_exceed_dose: boolean;
  has_not_replace_diet: boolean;
  has_keep_away_children: boolean;
}

// ==========================================
// QUICK CHECK RESPONSE
// ==========================================

/**
 * POST /api/check-label/quick
 *
 * ⚠️ УВАГА: поле `warnings` тут містить ЗАСТЕРЕЖЕННЯ З ЕТИКЕТКИ (рядки),
 * а не DosageWarning. У Full-відповіді воно перейменоване в `label_warnings`.
 */
export interface QuickCheckResponse {
  check_id: string;

  /** Плаский список з OCR, без мапінгу на БД. */
  ingredients: QuickIngredient[];

  product_info: {
    name: string | null;
    form: ProductForm | null;
    quantity: number | null;
    batch_number: string | null;
  };

  allergens: string[] | null;
  allergen_statement: string | null;
  mandatory_phrases: MandatoryPhrases | null;
  full_text: string | null;
  operator: Operator | null;

  /** Застереження З ЕТИКЕТКИ (рядки), НЕ DosageWarning. */
  warnings: string[] | null;

  daily_dose: string | null;
  storage: string | null;
  manufacturer: Manufacturer | null;
  shelf_life: string | null;
  tech_specs: string | null;

  extracted_at: string; // ISO datetime
}

// ==========================================
// FULL CHECK RESPONSE
// ==========================================

/**
 * POST /api/check-label/full
 * Body: { check_id: string }
 *
 * ⚠️ УВАГА на два різні поля:
 *   - `warnings` — DosageWarning[] (попередження з валідації доз)
 *   - `label_warnings` — string[] | null (застереження З ЕТИКЕТКИ)
 */
export interface FullCheckResponse {
  check_id: string;
  is_valid: boolean;

  product_info: {
    name: string | null;
    form: ProductForm | null;
    quantity: number | null;
    batch_number: string | null;
    ingredients: ParsedIngredient[];
  };

  operator: Operator | null;
  manufacturer: Manufacturer | null;
  mandatory_phrases: MandatoryPhrases | null;
  full_text: string | null;

  /** Застереження З ЕТИКЕТКИ (з OCR), НЕ результат валідації. */
  label_warnings: string[] | null;

  daily_dose: string | null;
  storage: string | null;
  shelf_life: string | null;
  tech_specs: string | null;
  allergens: string[] | null;
  allergen_statement: string | null;

  /** Критичні помилки з перевірки доз. */
  errors: DosageError[];

  /** Попередження з перевірки доз (дози не встановлено, форма невірна тощо). */
  warnings: DosageWarning[];

  /** Помилки compliance (заборонені фрази + відсутні обов'язкові поля). */
  compliance_errors: ComplianceError[];

  stats: {
    total_ingredients: number;
    substances_not_found: number;
    total_dosage_errors: number;
    total_dosage_warnings: number;
    total_forbidden_phrases: number;
    total_missing_fields: number;
  };

  penalties: {
    dosage_penalties: number;
    compliance_penalties: number;
    total_amount: number;
    currency: 'UAH';
  };

  checked_at: string; // ISO datetime
}

// ==========================================
// API ERRORS
// ==========================================

/**
 * FastAPI за замовчуванням повертає { detail: string } для HTTPException.
 */
export interface APIErrorResponse {
  detail: string;
}

// ==========================================
// FRONT-ONLY STATES
// ==========================================

/**
 * Стани UI сторінки /checker. Використовувати в useState<CheckerState>.
 */
export type CheckerState =
  | { kind: 'idle' }
  | { kind: 'file_selected'; file: File; previewUrl: string | null }
  | { kind: 'quick_loading'; file: File; previewUrl: string | null; abort: AbortController }
  | { kind: 'full_loading'; file: File; previewUrl: string | null; quick: QuickCheckResponse; abort: AbortController }
  | { kind: 'success'; result: FullCheckResponse; file: File; previewUrl: string | null }
  | { kind: 'error'; reason: CheckerErrorReason; retryPayload?: { file?: File; check_id?: string } };

export type CheckerErrorReason =
  | 'file_too_large'
  | 'invalid_format'
  | 'quick_failed'
  | 'quick_timeout'
  | 'full_session_not_found'
  | 'full_failed'
  | 'network_error'
  | 'api_url_missing';

/**
 * Загальний overall-статус для StatusHero.
 */
export type OverallStatus = 'valid' | 'warnings_only' | 'has_errors';

export function computeOverallStatus(result: FullCheckResponse): OverallStatus {
  const hasErrors = result.errors.length > 0 || result.compliance_errors.length > 0;
  if (hasErrors) return 'has_errors';
  if (result.warnings.length > 0) return 'warnings_only';
  return 'valid';
}
