import { 
  Shield, 
  AlertTriangle, 
  FileText, 
  Scale, 
  Clock, 
  Download 
} from 'lucide-react';
import { content } from '@/content/ua';

const iconMap = {
  Shield: Shield,
  AlertTriangle: AlertTriangle,
  FileText: FileText,
  Scale: Scale,
  Clock: Clock,
  Download: Download,
};

export function Features() {
  return (
    <section className="py-16 md:py-24 bg-slate-50">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="text-center mb-12 md:mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">
            {content.features.title}
          </h2>
          <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
            {content.features.subtitle}
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {content.features.items.map((feature, index) => {
            const IconComponent = iconMap[feature.icon as keyof typeof iconMap];
            return (
              <div
                key={index}
                className="bg-white rounded-2xl p-6 shadow-sm hover:shadow-md transition-shadow"
              >
                {/* Icon */}
                <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center mb-4">
                  {IconComponent && (
                    <IconComponent className="h-6 w-6 text-white" />
                  )}
                </div>

                {/* Content */}
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {feature.title}
                </h3>
                <p className="text-muted-foreground text-sm leading-relaxed">
                  {feature.description}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}


