import Link from 'next/link';
import { ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { content } from '@/content/ua';

export function CTASection() {
  return (
    <section className="py-16 md:py-24">
      <div className="container mx-auto px-4">
        <div className="relative bg-gradient-primary rounded-3xl overflow-hidden">
          {/* Background decoration */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <div className="absolute -top-20 -right-20 w-60 h-60 bg-white/10 rounded-full blur-2xl" />
            <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-white/10 rounded-full blur-2xl" />
          </div>

          <div className="relative px-6 py-12 md:px-12 md:py-16 text-center">
            <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold text-white mb-4">
              {content.cta.title}
            </h2>
            <p className="text-white/80 text-lg mb-8 max-w-xl mx-auto">
              {content.cta.subtitle}
            </p>
            <Button
              asChild
              size="lg"
              className="bg-white text-primary hover:bg-white/90 px-8 h-12 text-base font-semibold"
            >
              <Link href="/checker">
                {content.cta.button}
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
}


