'use client';

import { FileText, Check, X } from 'lucide-react';
import { cn } from '@/lib/utils';
import type {
  Operator,
  Manufacturer,
  MandatoryPhrases,
  FullCheckResponse,
} from '@/lib/types';
import { CollapsibleSection } from './CollapsibleSection';

interface LabelMetadataSectionProps {
  result: FullCheckResponse;
}

const MANDATORY_PHRASE_LABELS: Array<{ key: keyof MandatoryPhrases; label: string }> = [
  { key: 'has_dietary_supplement_label', label: 'Маркування «Дієтична добавка»' },
  { key: 'has_not_medicine', label: '«Не є лікарським засобом»' },
  { key: 'has_not_exceed_dose', label: '«Не перевищувати рекомендовану добову дозу»' },
  { key: 'has_not_replace_diet', label: '«Не замінює повноцінне харчування»' },
  { key: 'has_keep_away_children', label: '«Зберігати в недоступному для дітей місці»' },
];

export function LabelMetadataSection({ result }: LabelMetadataSectionProps) {
  return (
    <CollapsibleSection title="Дані з етикетки" icon={FileText}>
      <div className="space-y-4">
        {result.operator && <OperatorBlock operator={result.operator} />}
        {result.manufacturer && <ManufacturerBlock manufacturer={result.manufacturer} />}

        <InfoGrid
          items={[
            { label: 'Добова доза', value: result.daily_dose },
            { label: 'Умови зберігання', value: result.storage },
            { label: 'Термін придатності', value: result.shelf_life },
            { label: 'Технічні характеристики', value: result.tech_specs },
          ]}
        />

        {result.allergens && result.allergens.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
              Алергени
            </p>
            <div className="flex flex-wrap gap-1.5">
              {result.allergens.map((a, i) => (
                <span
                  key={i}
                  className="text-xs px-2 py-1 rounded-full bg-warning-light text-warning-700 border border-warning/30"
                >
                  {a}
                </span>
              ))}
            </div>
            {result.allergen_statement && (
              <p className="text-xs text-muted-foreground mt-2 italic">
                «{result.allergen_statement}»
              </p>
            )}
          </div>
        )}

        {result.mandatory_phrases && (
          <MandatoryPhrasesBlock phrases={result.mandatory_phrases} />
        )}

        {result.label_warnings && result.label_warnings.length > 0 && (
          <div>
            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
              Застереження з етикетки
            </p>
            <ul className="space-y-1">
              {result.label_warnings.map((w, i) => (
                <li key={i} className="text-sm text-foreground flex items-start gap-2">
                  <span className="text-muted-foreground">•</span>
                  <span>{w}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </CollapsibleSection>
  );
}

function OperatorBlock({ operator }: { operator: Operator }) {
  const hasAny = operator.name || operator.edrpou || operator.address || operator.phone;
  if (!hasAny) return null;

  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
        Оператор ринку
      </p>
      <div className="space-y-1 text-sm">
        {operator.name && (
          <p>
            <span className="text-muted-foreground">Назва:</span>{' '}
            <span className="text-foreground">{operator.name}</span>
          </p>
        )}
        {operator.edrpou && (
          <p>
            <span className="text-muted-foreground">ЄДРПОУ:</span>{' '}
            <span className="text-foreground font-mono">{operator.edrpou}</span>
          </p>
        )}
        {operator.address && (
          <p>
            <span className="text-muted-foreground">Адреса:</span>{' '}
            <span className="text-foreground">{operator.address}</span>
          </p>
        )}
        {operator.phone && (
          <p>
            <span className="text-muted-foreground">Телефон:</span>{' '}
            <span className="text-foreground">{operator.phone}</span>
          </p>
        )}
      </div>
    </div>
  );
}

function ManufacturerBlock({ manufacturer }: { manufacturer: Manufacturer }) {
  const hasAny = manufacturer.name || manufacturer.address;
  if (!hasAny) return null;

  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
        Виробник
      </p>
      <div className="space-y-1 text-sm">
        {manufacturer.name && (
          <p>
            <span className="text-muted-foreground">Назва:</span>{' '}
            <span className="text-foreground">{manufacturer.name}</span>
          </p>
        )}
        {manufacturer.address && (
          <p>
            <span className="text-muted-foreground">Адреса:</span>{' '}
            <span className="text-foreground">{manufacturer.address}</span>
          </p>
        )}
      </div>
    </div>
  );
}

function InfoGrid({ items }: { items: Array<{ label: string; value: string | null }> }) {
  const present = items.filter((i) => i.value);
  if (present.length === 0) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {present.map((item) => (
        <div key={item.label}>
          <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-1">
            {item.label}
          </p>
          <p className="text-sm text-foreground">{item.value}</p>
        </div>
      ))}
    </div>
  );
}

function MandatoryPhrasesBlock({ phrases }: { phrases: MandatoryPhrases }) {
  return (
    <div>
      <p className="text-xs font-medium text-muted-foreground uppercase tracking-wide mb-2">
        Обов&apos;язкові фрази
      </p>
      <ul className="space-y-1.5">
        {MANDATORY_PHRASE_LABELS.map(({ key, label }) => {
          const present = phrases[key];
          return (
            <li key={key} className="flex items-start gap-2 text-sm">
              {present ? (
                <Check className="h-4 w-4 text-success flex-shrink-0 mt-0.5" />
              ) : (
                <X className="h-4 w-4 text-error flex-shrink-0 mt-0.5" />
              )}
              <span
                className={cn(
                  present ? 'text-foreground' : 'text-muted-foreground line-through'
                )}
              >
                {label}
              </span>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
