'use client';

import Link from 'next/link';
import { ArrowRight, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { content } from '@/content/ua';

export function HeroSection() {
  return (
    <section className="relative min-h-[calc(100vh-64px)] bg-gradient-hero overflow-hidden">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary/5 rounded-full blur-3xl" />
        <div className="absolute top-1/2 -left-40 w-80 h-80 bg-cyan-500/5 rounded-full blur-3xl" />
      </div>

      <div className="container mx-auto px-4 pt-16 pb-24 md:pt-24 md:pb-32 relative">
        <div className="max-w-4xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-8 animate-fade-in">
            <Sparkles className="h-4 w-4" />
            <span className="text-sm font-medium">{content.hero.badge}</span>
          </div>

          {/* Title */}
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-foreground mb-6 animate-fade-in">
            {content.hero.title}{' '}
            <span className="text-gradient">{content.hero.titleHighlight}</span>
          </h1>

          {/* Subtitle */}
          <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-10 animate-fade-in">
            {content.hero.subtitle}
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16 animate-slide-up">
            <Button
              asChild
              size="lg"
              className="w-full sm:w-auto bg-gradient-primary hover:opacity-90 text-white px-8 h-12 text-base"
            >
              <Link href="/checker">
                {content.hero.primaryCta}
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button
              asChild
              variant="outline"
              size="lg"
              className="w-full sm:w-auto px-8 h-12 text-base"
            >
              <Link href="/#how-it-works">{content.hero.secondaryCta}</Link>
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-4 md:gap-8 max-w-xl mx-auto animate-slide-up">
            <div className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-foreground">
                {content.hero.stats.checks}
              </div>
              <div className="text-sm text-muted-foreground">
                {content.hero.stats.checksLabel}
              </div>
            </div>
            <div className="text-center border-x border-border">
              <div className="text-2xl md:text-3xl font-bold text-foreground">
                {content.hero.stats.accuracy}
              </div>
              <div className="text-sm text-muted-foreground">
                {content.hero.stats.accuracyLabel}
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl md:text-3xl font-bold text-foreground">
                {content.hero.stats.time}
              </div>
              <div className="text-sm text-muted-foreground">
                {content.hero.stats.timeLabel}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}


