'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { useToast } from '@/hooks/use-toast';
import { AIReasoningDisplay } from '@/components/ai/AIReasoningDisplay';
import { Loader2, ArrowLeft, Check, Globe, Rss, Database, User } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useTranslations } from 'next-intl';

// Types (should be in a types file, but defining here for now or importing if available)
interface SourceAnalyzeResponse {
  title: string;
  summary: string;
  tags: string[];
  suggested_node_id?: string;
  reasoning?: string;
  confidence?: number;
}

export default function SourceAddPage() {
  const t = useTranslations('Sources.Add');
  const tCommon = useTranslations('Common');
  const router = useRouter();
  const { toast } = useToast();
  
  const [step, setStep] = useState<'input' | 'analyzing' | 'review'>('input');
  const [url, setUrl] = useState('');
  const [isThinking, setIsThinking] = useState(false);
  const [analysis, setAnalysis] = useState<SourceAnalyzeResponse | null>(null);
  
  // Form data
  const [name, setName] = useState('');
  const [type, setType] = useState('WEB');
  const [checkInterval, setCheckInterval] = useState('3600');
  
  const handleAnalyze = async () => {
    if (!url) {
      toast({ title: t('alerts.input_url'), variant: 'destructive' });
      return;
    }
    
    // Simple regex to guess type (optional enhancement)
    if (url.endsWith('.xml') || url.includes('rss') || url.includes('feed')) {
        setType('RSS');
    }

    setStep('analyzing');
    setIsThinking(true);
    
    try {
      const res = await fetch('/api/v1/sources/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      
      if (!res.ok) throw new Error(t('alerts.analyze_failed'));
      
      const data = await res.json();
      if (data.success) {
        setAnalysis(data.data);
        setName(data.data.title || '');
        setStep('review');
      } else {
        throw new Error(data.error?.message || t('alerts.analyze_failed'));
      }
    } catch (error: any) {
      toast({ title: t('alerts.analyze_error'), description: error.message, variant: 'destructive' });
      setStep('input');
    } finally {
      setIsThinking(false);
    }
  };
  
  const handleSubmit = async () => {
    try {
      const res = await fetch('/api/v1/sources', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          url,
          type,
          check_interval: parseInt(checkInterval),
          config: {}, // Empty config for now
        }),
      });
      
      if (!res.ok) throw new Error(t('alerts.create_error'));
      
      const data = await res.json();
      if (data.success) {
        toast({ title: t('alerts.success') });
        router.push('/sources');
      }
    } catch (error: any) {
      toast({ title: t('alerts.create_error'), description: error.message, variant: 'destructive' });
    }
  };

  return (
    <div className="container max-w-3xl py-8 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.back()}>
          <ArrowLeft className="h-4 w-4" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold tracking-tight">{t('title')}</h1>
          <p className="text-muted-foreground">{t('description')}</p>
        </div>
      </div>

      <div className="grid gap-6">
        {step === 'input' && (
            <Card>
                <CardHeader>
                    <CardTitle>{t('url_card.title')}</CardTitle>
                    <CardDescription>{t('url_card.description')}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="url">{t('url_card.label')}</Label>
                        <Input 
                            id="url" 
                            placeholder={t('url_card.placeholder')}
                            value={url} 
                            onChange={(e) => setUrl(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleAnalyze()}
                        />
                    </div>
                </CardContent>
                <CardFooter>
                    <Button onClick={handleAnalyze} className="w-full" disabled={!url}>
                        {t('url_card.analyze_btn')}
                    </Button>
                </CardFooter>
            </Card>
        )}

        {step === 'analyzing' && (
            <Card>
                <CardHeader>
                    <CardTitle>{t('analyzing_card.title')}</CardTitle>
                    <CardDescription>{t('analyzing_card.description')}</CardDescription>
                </CardHeader>
                <CardContent>
                    <AIReasoningDisplay 
                        isThinking={isThinking}
                        steps={[
                            t('analyzing_card.steps.fetching'),
                            t('analyzing_card.steps.analyzing'),
                            t('analyzing_card.steps.evaluating'),
                            t('analyzing_card.steps.generating')
                        ]}
                        currentStep={isThinking ? 1 : 4} 
                    />
                </CardContent>
            </Card>
        )}

        {step === 'review' && analysis && (
            <div className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>{t('review_card.title')}</CardTitle>
                        <CardDescription>{t('review_card.description')}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {/* AI Insights */}
                        <div className="bg-muted/50 p-4 rounded-lg space-y-3">
                            <div className="flex items-center gap-2 text-sm font-medium text-primary">
                                <Loader2 className="h-4 w-4 animate-spin" /> 
                                {t('review_card.ai_analysis')}
                            </div>
                            <div className="text-sm text-muted-foreground">
                                {analysis.reasoning || t('review_card.analysis_complete')}
                            </div>
                            <div className="flex flex-wrap gap-2">
                                {analysis.tags.map(tag => (
                                    <Badge key={tag} variant="secondary">{tag}</Badge>
                                ))}
                            </div>
                            {analysis.confidence && (
                                <div className="text-xs text-muted-foreground">
                                    {t('review_card.confidence')}: {(analysis.confidence * 100).toFixed(0)}%
                                </div>
                            )}
                        </div>

                        {/* Configuration Form */}
                        <div className="grid gap-4">
                            <div className="space-y-2">
                                <Label htmlFor="name">{t('review_card.name_label')}</Label>
                                <Input 
                                    id="name" 
                                    value={name} 
                                    onChange={(e) => setName(e.target.value)} 
                                />
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="space-y-2">
                                    <Label htmlFor="type">{t('review_card.type_label')}</Label>
                                    <Select value={type} onValueChange={setType}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="WEB">
                                                <div className="flex items-center gap-2"><Globe className="h-4 w-4"/> {t('review_card.types.web')}</div>
                                            </SelectItem>
                                            <SelectItem value="RSS">
                                                <div className="flex items-center gap-2"><Rss className="h-4 w-4"/> {t('review_card.types.rss')}</div>
                                            </SelectItem>
                                            <SelectItem value="API">
                                                <div className="flex items-center gap-2"><Database className="h-4 w-4"/> {t('review_card.types.api')}</div>
                                            </SelectItem>
                                            <SelectItem value="USER">
                                                <div className="flex items-center gap-2"><User className="h-4 w-4"/> {t('review_card.types.user')}</div>
                                            </SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label htmlFor="interval">{t('review_card.interval_label')}</Label>
                                    <Select value={checkInterval} onValueChange={setCheckInterval}>
                                        <SelectTrigger>
                                            <SelectValue />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="3600">{t('review_card.intervals.hourly')}</SelectItem>
                                            <SelectItem value="14400">{t('review_card.intervals.every_4h')}</SelectItem>
                                            <SelectItem value="43200">{t('review_card.intervals.every_12h')}</SelectItem>
                                            <SelectItem value="86400">{t('review_card.intervals.daily')}</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>
                            </div>
                            
                            <div className="space-y-2">
                                <Label>{t('review_card.summary_label')}</Label>
                                <p className="text-sm text-muted-foreground p-2 border rounded-md bg-background">
                                    {analysis.summary || t('review_card.no_summary')}
                                </p>
                            </div>
                        </div>
                    </CardContent>
                    <CardFooter className="flex justify-between">
                        <Button variant="outline" onClick={() => setStep('input')}>{tCommon('back')}</Button>
                        <Button onClick={handleSubmit}>
                            <Check className="mr-2 h-4 w-4" /> {t('review_card.confirm_btn')}
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        )}
      </div>
    </div>
  );
}
