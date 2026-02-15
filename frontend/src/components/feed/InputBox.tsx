'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AIReasoningDisplay } from '@/components/ai/AIReasoningDisplay';
import { Loader2, Send, Sparkles, Link as LinkIcon, FileText, X } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { Badge } from '@/components/ui/badge';

interface ClassificationResult {
  suggested_node_id?: string;
  reasoning?: string;
  confidence?: number;
  tags: string[];
}

export function InputBox({ onContentAdded }: { onContentAdded?: () => void }) {
  const t = useTranslations('Feed.InputBox');
  const { toast } = useToast();
  const [activeTab, setActiveTab] = useState<'text' | 'url'>('text');
  
  // Inputs
  const [text, setText] = useState('');
  const [title, setTitle] = useState('');
  const [url, setUrl] = useState('');
  
  // AI State
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ClassificationResult | null>(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAnalyze = async () => {
    const contentToAnalyze = activeTab === 'text' ? text : url;
    const titleToAnalyze = activeTab === 'text' ? title : '';
    
    if (!contentToAnalyze) return;

    setIsAnalyzing(true);
    setAnalysis(null);
    setIsExpanded(true);

    try {
      const res = await fetch('/api/v1/contents/classify', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: contentToAnalyze,
          title: titleToAnalyze
        }),
      });

      if (!res.ok) throw new Error('Classification failed');
      const data = await res.json();
      if (data.success) {
        setAnalysis(data.data);
      }
    } catch (error) {
      console.error(error);
      toast({ title: t('analyze_failed'), variant: 'destructive' });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    try {
      let endpoint = '';
      let body = {};
      
      if (activeTab === 'text') {
        endpoint = '/api/v1/contents/text';
        body = { text, title, submitter_id: 'user' }; // Hardcoded user for now
      } else {
        endpoint = '/api/v1/contents/url';
        body = { url, submitter_id: 'user' };
      }

      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });

      if (!res.ok) throw new Error('Submission failed');
      const data = await res.json();
      
      if (data.success) {
        toast({ title: t('submit_success') });
        // Reset form
        setText('');
        setTitle('');
        setUrl('');
        setAnalysis(null);
        setIsExpanded(false);
        if (onContentAdded) onContentAdded();
      }
    } catch (error) {
      toast({ title: t('submit_failed'), variant: 'destructive' });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className="w-full mb-6 border-2 border-muted/40 hover:border-primary/20 transition-colors">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-center">
            <CardTitle className="text-lg flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-primary" />
                {t('title')}
            </CardTitle>
        </div>
      </CardHeader>
      <CardContent className="pb-3">
        <Tabs value={activeTab} onValueChange={(v: any) => setActiveTab(v)} className="w-full">
          <TabsList className="grid w-full grid-cols-2 mb-4">
            <TabsTrigger value="text"><FileText className="h-4 w-4 mr-2"/> {t('text_tab')}</TabsTrigger>
            <TabsTrigger value="url"><LinkIcon className="h-4 w-4 mr-2"/> {t('url_tab')}</TabsTrigger>
          </TabsList>
          
          <TabsContent value="text" className="space-y-4">
            <Input 
                placeholder={t('title_placeholder')} 
                value={title} 
                onChange={e => setTitle(e.target.value)} 
            />
            <Textarea 
                placeholder={t('content_placeholder')} 
                className="min-h-[100px]"
                value={text}
                onChange={e => setText(e.target.value)}
            />
          </TabsContent>
          
          <TabsContent value="url" className="space-y-4">
            <Input 
                placeholder={t('url_placeholder')} 
                value={url} 
                onChange={e => setUrl(e.target.value)} 
            />
            <p className="text-sm text-muted-foreground">
                {t('url_hint')}
            </p>
          </TabsContent>
        </Tabs>

        {/* AI Analysis Section */}
        {isExpanded && (
            <div className="mt-4 border-t pt-4 animate-in slide-in-from-top-2 fade-in">
                {isAnalyzing ? (
                    <AIReasoningDisplay 
                        isThinking={true}
                        steps={[t('ai_steps.reading'), t('ai_steps.concepts'), t('ai_steps.relations'), t('ai_steps.classifying')]}
                        currentStep={2}
                    />
                ) : analysis ? (
                    <div className="bg-muted/30 p-3 rounded-md space-y-2">
                        <div className="flex items-center justify-between">
                            <span className="text-sm font-medium text-primary flex items-center gap-2">
                                <Sparkles className="h-3 w-3" /> {t('ai_analysis')}
                            </span>
                            <span className="text-xs text-muted-foreground">
                                {t('confidence')}: {(analysis.confidence || 0) * 100}%
                            </span>
                        </div>
                        <p className="text-sm text-muted-foreground">{analysis.reasoning}</p>
                        <div className="flex flex-wrap gap-2">
                            {analysis.tags.map(tag => (
                                <Badge key={tag} variant="outline" className="bg-background">{tag}</Badge>
                            ))}
                        </div>
                    </div>
                ) : null}
            </div>
        )}
      </CardContent>
      <CardFooter className="flex justify-between pt-0">
        <Button variant="ghost" onClick={() => setIsExpanded(false)} disabled={!isExpanded}>
            <X className="h-4 w-4 mr-2" /> {t('cancel')}
        </Button>
        <div className="flex gap-2">
            <Button 
                variant="outline" 
                onClick={handleAnalyze} 
                disabled={isAnalyzing || (!text && !url)}
            >
                <Sparkles className="h-4 w-4 mr-2" /> {t('analyze_first')}
            </Button>
            <Button onClick={handleSubmit} disabled={isSubmitting || (!text && !url)}>
                {isSubmitting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4 mr-2" />}
                {t('submit')}
            </Button>
        </div>
      </CardFooter>
    </Card>
  );
}
