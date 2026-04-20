/**
 * Людські ярлики для технічних значень з бекенду.
 *
 * Бек повертає в полях `source` / `regulatory_source` / `article_number`
 * рядки, зручні для обробки, але не для UI. Ці функції форматують їх
 * для відображення.
 */

import type { DosageSource } from './types';

/**
 * Мапа DosageSource (відомі значення) → українська назва джерела.
 * Для невідомих ключів повертаємо сирий рядок без зміни.
 */
const DOSAGE_SOURCE_LABELS: Record<string, string> = {
  efsa_ul: 'EFSA Upper Limit',
  efsa_safe: 'EFSA Safe Level',
  table1: 'Таблиця 1 Наказу МОЗ №1114',
  amino_acids_table: 'Таблиця амінокислот',
  allowed_plants: 'Перелік дозволених рослин',
  microorganisms: 'Перелік мікроорганізмів',
  physiological_table: 'Таблиця фізіологічних речовин',
  novel_foods: 'Novel foods',
  other_substances: 'Інші речовини',
  banned_substances: 'Заборонені речовини',
  no_limit_available: 'Ліміт не встановлено',
  unknown: 'Невідоме джерело',
};

/**
 * Форматує `DosageSource` для UI.
 * Повертає null якщо вхід null.
 */
export function formatDosageSource(source: DosageSource | null): string | null {
  if (!source) return null;
  return DOSAGE_SOURCE_LABELS[source] ?? source;
}

/**
 * Формує рядок "Джерело: {regulatory_source}, ст. {article_number}".
 *
 * Важливо: бек іноді кладе номер статті вже в `regulatory_source`
 * (напр. "Закон №2639-VIII, ст.6, п.8"), і тоді дописувати його ще раз —
 * дубль. Перевіряємо це через підрядок та ігноруємо article_number,
 * якщо він уже є в regulatory_source.
 */
export function formatRegulatorySource(
  regulatorySource: string,
  articleNumber: string | null
): string {
  if (!articleNumber) return regulatorySource;

  const normalized = articleNumber.trim();
  if (!normalized) return regulatorySource;

  if (regulatorySource.includes(normalized)) {
    return regulatorySource;
  }

  return `${regulatorySource}, ст. ${normalized}`;
}
