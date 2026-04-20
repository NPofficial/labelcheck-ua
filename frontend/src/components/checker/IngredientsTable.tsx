'use client';

import { useState } from 'react';
import { CheckCircle2, XCircle, ChevronDown, ChevronUp, List } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { ParsedIngredient } from '@/lib/types';

interface IngredientsTableProps {
  ingredients: ParsedIngredient[];
  /** Скільки рядків показати за замовчуванням (решта — під "Показати ще"). */
  defaultVisible?: number;
}

const TYPE_LABELS: Record<string, { label: string; className: string }> = {
  active: { label: 'Активна', className: 'bg-primary text-white' },
  excipient: { label: 'Допоміжна', className: 'bg-muted text-foreground' },
  plant: { label: 'Рослина', className: 'bg-success text-white' },
};

const SOURCE_LABELS: Record<string, string> = {
  excipients_db: 'БД допоміжних',
  allowed_plants: 'Дозволені рослини',
};

function formatQuantity(ing: ParsedIngredient): string {
  const main = ing.quantity !== null ? `${ing.quantity} ${ing.unit}` : '—';
  if (ing.elemental_quantity !== null && ing.elemental_quantity !== ing.quantity) {
    return `${main} (елем. ${ing.elemental_quantity} ${ing.unit})`;
  }
  return main;
}

export function IngredientsTable({
  ingredients,
  defaultVisible = 5,
}: IngredientsTableProps) {
  const [expanded, setExpanded] = useState(false);

  if (!ingredients || ingredients.length === 0) {
    return null;
  }

  const visible = expanded ? ingredients : ingredients.slice(0, defaultVisible);
  const hidden = ingredients.length - visible.length;

  return (
    <section>
      <h3 className="text-lg font-semibold text-foreground mb-4 flex items-center gap-2">
        <List className="h-5 w-5 text-primary" />
        Розпізнані інгредієнти ({ingredients.length})
      </h3>

      <div className="space-y-2">
        {visible.map((ing, index) => (
          <IngredientRow key={`ing-${index}`} ingredient={ing} />
        ))}
      </div>

      {ingredients.length > defaultVisible && (
        <button
          onClick={() => setExpanded((e) => !e)}
          className="mt-3 w-full flex items-center justify-center gap-2 py-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          {expanded ? (
            <>
              Згорнути <ChevronUp className="h-4 w-4" />
            </>
          ) : (
            <>
              Показати ще {hidden} <ChevronDown className="h-4 w-4" />
            </>
          )}
        </button>
      )}
    </section>
  );
}

function IngredientRow({ ingredient }: { ingredient: ParsedIngredient }) {
  const typeMeta = ingredient.type ? TYPE_LABELS[ingredient.type] : null;
  const sourceLabel = ingredient.source ? SOURCE_LABELS[ingredient.source] ?? ingredient.source : null;

  return (
    <div
      className={cn(
        'rounded-lg border p-3 bg-white',
        ingredient.found ? 'border-muted' : 'border-warning/30 bg-warning-light/40'
      )}
    >
      <div className="flex items-start justify-between gap-3 flex-wrap">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            {ingredient.found ? (
              <CheckCircle2 className="h-4 w-4 text-success flex-shrink-0" />
            ) : (
              <XCircle className="h-4 w-4 text-warning flex-shrink-0" />
            )}
            <span className="font-medium text-foreground">{ingredient.name}</span>
            {typeMeta && (
              <span
                className={cn(
                  'text-xs px-2 py-0.5 rounded-full font-medium',
                  typeMeta.className
                )}
              >
                {typeMeta.label}
              </span>
            )}
            {ingredient.is_extract && (
              <span className="text-xs px-2 py-0.5 rounded-full font-medium bg-accent text-foreground border">
                Екстракт{ingredient.ratio ? ` ${ingredient.ratio}` : ''}
              </span>
            )}
          </div>

          {ingredient.base_substance && ingredient.base_substance !== ingredient.name && (
            <p className="text-xs text-muted-foreground mt-1 ml-6">
              Базова речовина: <span className="text-foreground">{ingredient.base_substance}</span>
              {ingredient.form ? (
                <>
                  {' · '}Форма: <span className="text-foreground">{ingredient.form}</span>
                </>
              ) : null}
            </p>
          )}

          {ingredient._from_composition && (
            <p className="text-xs text-muted-foreground mt-1 ml-6 italic">
              із композиції: {ingredient._from_composition}
            </p>
          )}

          {sourceLabel && (
            <p className="text-[11px] text-muted-foreground mt-1 ml-6">
              Джерело: {sourceLabel}
            </p>
          )}
        </div>

        <div className="flex-shrink-0 text-right">
          <p className="text-sm font-semibold text-foreground">{formatQuantity(ingredient)}</p>
        </div>
      </div>
    </div>
  );
}
