'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { AIReasoningDisplay } from '@/components/ai/AIReasoningDisplay';
import { PyramidPreview } from '@/components/ai/PyramidPreview';
import { Loader2, ArrowLeft, Wand2, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { useTranslations } from 'next-intl';

export default function CreatePyramidPage() {
  const t = useTranslations('Pyramid.Create');
  const router = useRouter();
  const { toast } = useToast();
  
  const [step, setStep] = useState<'input' | 'analyzing' | 'review' | 'creating'>('input');
  const [formData, setFormData] = useState({ name: '', description: '' });
  const [suggestion, setSuggestion] = useState<any>(null);
  const [isThinking, setIsThinking] = useState(false);

  const handleGenerate = async () => {
    if (!formData.name || !formData.description) {
      toast({ title: t('alerts.fill_required'), variant: 'destructive' });
      return;
    }

    setStep('analyzing');
    setIsThinking(true);

    try {
      const res = await fetch('/api/v1/pyramids/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData),
      });

      if (!res.ok) throw new Error(t('alerts.generate_failed'));

      const data = await res.json();
      if (data.success) {
        setSuggestion(data.data);
        setStep('review');
      } else {
        throw new Error(data.error?.message || t('alerts.unknown_error'));
      }
    } catch (error: any) {
      toast({ title: t('alerts.generate_error'), description: error.message, variant: 'destructive' });
      setStep('input');
    } finally {
      setIsThinking(false);
    }
  };

  const handleConfirm = async () => {
    if (!suggestion) return;

    setStep('creating');
    try {
      const res = await fetch('/api/v1/pyramids/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          suggestion_id: suggestion.suggestion_id,
          // modifications: ... // If we supported editing in preview
        }),
      });

      if (!res.ok) throw new Error(t('alerts.create_failed'));

      const data = await res.json();
      if (data.success) {
        toast({ title: t('alerts.create_success') });
        router.push(`/pyramid/${data.data.id}`);
      } else {
        throw new Error(data.error?.message || t('alerts.unknown_error'));
      }
    } catch (error: any) {
      toast({ title: t('alerts.create_error'), description: error.message, variant: 'destructive' });
      setStep('review');
    }
  };

  return (
    <div className="container mx-auto py-8 max-w-4xl">
      <Button variant="ghost" className="mb-4" onClick={() => router.back()}>
        <ArrowLeft className="mr-2 h-4 w-4" /> {t('back')}
      </Button>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>{t('title')}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('name_label')}</label>
              <Input
                placeholder={t('name_placeholder')}
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                disabled={step !== 'input'}
              />
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">{t('desc_label')}</label>
              <Textarea
                placeholder={t('desc_placeholder')}
                className="h-32"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                disabled={step !== 'input'}
              />
            </div>
          </CardContent>
          <CardFooter>
            {step === 'input' && (
              <Button onClick={handleGenerate} className="w-full" disabled={!formData.name || !formData.description}>
                <Wand2 className="mr-2 h-4 w-4" /> {t('generate_btn')}
              </Button>
            )}
          </CardFooter>
        </Card>

        {/* AI Reasoning Display */}
        {(step === 'analyzing' || step === 'review' || step === 'creating') && (
          <AIReasoningDisplay
            isThinking={isThinking}
            reasoning={suggestion?.reasoning}
          />
        )}

        {/* Suggestion Preview */}
        {(step === 'review' || step === 'creating') && suggestion && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4">
            <PyramidPreview structure={suggestion.structure} />
            
            <div className="flex justify-end gap-4">
              <Button variant="outline" onClick={() => setStep('input')} disabled={step === 'creating'}>
                {t('modify_btn')}
              </Button>
              <Button onClick={handleConfirm} disabled={step === 'creating'}>
                {step === 'creating' ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" /> {t('creating')}
                  </>
                ) : (
                  <>
                    <Check className="mr-2 h-4 w-4" /> {t('confirm_btn')}
                  </>
                )}

              </Button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
