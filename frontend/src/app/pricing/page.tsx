'use client';

import { useState } from 'react';
import { Check, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';
import { content } from '@/content/ua';

export default function PricingPage() {
  const [isYearly, setIsYearly] = useState(false);

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gradient-hero">
      <div className="container mx-auto px-4 py-12 md:py-20">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl lg:text-5xl font-bold text-foreground mb-4">
            {content.pricing.title}
          </h1>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto mb-8">
            {content.pricing.subtitle}
          </p>

          {/* Toggle */}
          <div className="inline-flex items-center gap-4 p-1 bg-white rounded-full border shadow-sm">
            <button
              onClick={() => setIsYearly(false)}
              className={cn(
                'px-6 py-2 rounded-full text-sm font-medium transition-all',
                !isYearly
                  ? 'bg-primary text-white'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              {content.pricing.monthly}
            </button>
            <button
              onClick={() => setIsYearly(true)}
              className={cn(
                'px-6 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2',
                isYearly
                  ? 'bg-primary text-white'
                  : 'text-muted-foreground hover:text-foreground'
              )}
            >
              {content.pricing.yearly}
              <span className="px-2 py-0.5 bg-success text-white text-xs rounded-full">
                -20%
              </span>
            </button>
          </div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 lg:gap-8 max-w-6xl mx-auto">
          {content.pricing.plans.map((plan, index) => {
            const price = isYearly
              ? Math.round(Number(plan.price) * 0.8)
              : Number(plan.price);

            return (
              <div
                key={index}
                className={cn(
                  'relative bg-white rounded-2xl p-6 md:p-8 transition-all',
                  plan.popular
                    ? 'border-2 border-primary shadow-xl md:scale-105 md:-my-4'
                    : 'border shadow-sm hover:shadow-md'
                )}
              >
                {/* Popular Badge */}
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2">
                    <div className="inline-flex items-center gap-1.5 px-4 py-1.5 bg-gradient-primary text-white text-sm font-medium rounded-full">
                      <Sparkles className="h-4 w-4" />
                      Популярний
                    </div>
                  </div>
                )}

                {/* Plan Header */}
                <div className="text-center mb-6">
                  <h3 className="text-xl font-bold text-foreground mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {plan.description}
                  </p>
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl md:text-5xl font-bold text-foreground">
                      {price}
                    </span>
                    <span className="text-muted-foreground">{plan.period}</span>
                  </div>
                </div>

                {/* Features */}
                <ul className="space-y-4 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-start gap-3">
                      <div className="flex-shrink-0 w-5 h-5 rounded-full bg-success/10 flex items-center justify-center mt-0.5">
                        <Check className="h-3 w-3 text-success" />
                      </div>
                      <span className="text-sm text-foreground">{feature}</span>
                    </li>
                  ))}
                </ul>

                {/* CTA Button */}
                <Button
                  className={cn(
                    'w-full h-12',
                    plan.popular
                      ? 'bg-gradient-primary hover:opacity-90 text-white'
                      : 'bg-secondary text-foreground hover:bg-secondary/80'
                  )}
                >
                  {plan.cta}
                </Button>
              </div>
            );
          })}
        </div>

        {/* FAQ Section (optional) */}
        <div className="mt-20 text-center">
          <p className="text-muted-foreground">
            Маєте питання?{' '}
            <a href="#" className="text-primary hover:underline">
              Зв&apos;яжіться з нами
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}


