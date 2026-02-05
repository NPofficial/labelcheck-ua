import { Upload, ScanLine, FileCheck } from 'lucide-react';
import { content } from '@/content/ua';

const iconMap = {
  Upload: Upload,
  Scan: ScanLine,
  FileCheck: FileCheck,
};

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-16 md:py-24 bg-white">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12 md:mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            {content.howItWorks.title}
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            {content.howItWorks.subtitle}
          </p>
        </div>

        {/* Steps */}
        <div className="relative max-w-5xl mx-auto">
          {/* Connection Line (desktop only) */}
          <div className="hidden md:block absolute top-16 left-1/4 right-1/4 h-0.5 bg-gradient-to-r from-primary/20 via-primary/40 to-primary/20" />

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 md:gap-12">
            {content.howItWorks.steps.map((step) => {
              const IconComponent = iconMap[step.icon as keyof typeof iconMap];
              return (
                <div key={step.number} className="relative text-center">
                  {/* Icon Container */}
                  <div className="relative inline-flex mb-6">
                    <div className="w-16 h-16 rounded-2xl bg-gradient-primary flex items-center justify-center shadow-lg">
                      {IconComponent && (
                        <IconComponent className="h-8 w-8 text-white" />
                      )}
                    </div>
                    {/* Step Number Badge */}
                    <div className="absolute -top-2 -right-2 w-7 h-7 rounded-full bg-white border-2 border-primary flex items-center justify-center">
                      <span className="text-sm font-bold text-primary">
                        {step.number}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <h3 className="text-xl font-semibold text-foreground mb-3">
                    {step.title}
                  </h3>
                  <p className="text-muted-foreground leading-relaxed">
                    {step.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}


