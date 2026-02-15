import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BrainCircuit, Loader2 } from 'lucide-react';
import { useTranslations } from 'next-intl';

interface AIReasoningDisplayProps {
  reasoning?: string;
  isThinking?: boolean;
  className?: string;
  steps?: string[];
  currentStep?: number;
}

export function AIReasoningDisplay({ reasoning, isThinking, className, steps, currentStep }: AIReasoningDisplayProps) {
  const t = useTranslations('Components.AIReasoning');

  if (!reasoning && !isThinking && !steps) return null;

  return (
    <Card className={`bg-slate-50 border-blue-100 ${className}`}>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-blue-600 flex items-center gap-2">
          <BrainCircuit className="h-4 w-4" />
          {t('title')}
        </CardTitle>
      </CardHeader>
      <CardContent>
        {steps && steps.length > 0 && (
          <div className="space-y-2 mb-4">
            {steps.map((step, index) => (
              <div key={index} className="flex items-center gap-2 text-sm">
                 <div className={`h-2 w-2 rounded-full ${
                   (currentStep ?? -1) >= index ? 'bg-blue-500' : 'bg-slate-300'
                 }`} />
                 <span className={`${
                   (currentStep ?? -1) >= index ? 'text-slate-900 font-medium' : 'text-slate-400'
                 }`}>
                   {step}
                 </span>
                 {(currentStep === index && isThinking) && (
                   <Loader2 className="h-3 w-3 animate-spin text-blue-500" />
                 )}
              </div>
            ))}
          </div>
        )}
        {isThinking && !reasoning && !steps && (
          <div className="flex items-center gap-2 text-slate-500 text-sm">
            <Loader2 className="h-3 w-3 animate-spin" />
            {t('analyzing')}
          </div>
        )}
        {reasoning && (
          <div className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">
            {reasoning}
            {isThinking && (
              <span className="inline-block w-1.5 h-3 ml-1 bg-blue-400 animate-pulse align-middle" />
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
