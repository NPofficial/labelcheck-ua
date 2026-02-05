'use client';

import { useState } from 'react';
import { Sparkles, Bell, ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { content } from '@/content/ua';

export default function GeneratorPage() {
  const [email, setEmail] = useState('');
  const [isSubmitted, setIsSubmitted] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement email subscription
    console.log('Subscribe:', email);
    setIsSubmitted(true);
  };

  return (
    <div className="min-h-[calc(100vh-64px)] bg-gradient-hero flex items-center">
      <div className="container mx-auto px-4 py-12">
        <div className="max-w-xl mx-auto text-center">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-primary mb-8">
            <Sparkles className="h-10 w-10 text-white" />
          </div>

          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary/10 text-primary mb-6">
            <span className="text-sm font-medium">{content.generator.subtitle}</span>
          </div>

          {/* Title */}
          <h1 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            {content.generator.title}
          </h1>

          {/* Description */}
          <p className="text-lg text-muted-foreground mb-8">
            {content.generator.description}
          </p>

          {/* Email Form */}
          {!isSubmitted ? (
            <form onSubmit={handleSubmit} className="max-w-md mx-auto">
              <div className="flex flex-col sm:flex-row gap-3">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder={content.generator.emailPlaceholder}
                  required
                  className="flex-1 h-12 px-4 rounded-xl border border-gray-200 focus:border-primary focus:ring-2 focus:ring-primary/20 outline-none transition-all"
                />
                <Button
                  type="submit"
                  className="h-12 px-6 bg-gradient-primary hover:opacity-90 text-white whitespace-nowrap"
                >
                  <Bell className="mr-2 h-4 w-4" />
                  {content.generator.notify}
                </Button>
              </div>
            </form>
          ) : (
            <div className="p-6 bg-success-light rounded-2xl">
              <p className="text-success font-medium">
                ✓ Дякуємо! Ми повідомимо вас, коли генератор буде готовий.
              </p>
            </div>
          )}

          {/* Back Link */}
          <div className="mt-12">
            <Link
              href="/"
              className="inline-flex items-center gap-2 text-muted-foreground hover:text-primary transition-colors"
            >
              <ArrowLeft className="h-4 w-4" />
              Повернутися на головну
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}


