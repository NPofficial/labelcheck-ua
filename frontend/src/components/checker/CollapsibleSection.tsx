'use client';

import { useState, type ReactNode } from 'react';
import { ChevronDown, ChevronUp, type LucideIcon } from 'lucide-react';
import { cn } from '@/lib/utils';

interface CollapsibleSectionProps {
  title: string;
  icon?: LucideIcon;
  /** За замовчуванням згорнуто. */
  defaultOpen?: boolean;
  children: ReactNode;
  subtitle?: string;
}

export function CollapsibleSection({
  title,
  icon: Icon,
  defaultOpen = false,
  subtitle,
  children,
}: CollapsibleSectionProps) {
  const [open, setOpen] = useState(defaultOpen);

  return (
    <div className="rounded-xl border border-border overflow-hidden">
      <button
        onClick={() => setOpen((o) => !o)}
        className={cn(
          'w-full flex items-center justify-between p-4 bg-gray-50 hover:bg-gray-100 transition-colors text-left',
          open && 'border-b border-border'
        )}
        aria-expanded={open}
      >
        <div className="flex items-center gap-2">
          {Icon && <Icon className="h-5 w-5 text-muted-foreground" />}
          <div>
            <p className="font-medium text-foreground">{title}</p>
            {subtitle && <p className="text-xs text-muted-foreground">{subtitle}</p>}
          </div>
        </div>
        {open ? (
          <ChevronUp className="h-5 w-5 text-muted-foreground flex-shrink-0" />
        ) : (
          <ChevronDown className="h-5 w-5 text-muted-foreground flex-shrink-0" />
        )}
      </button>

      {open && <div className="p-4 bg-white">{children}</div>}
    </div>
  );
}
