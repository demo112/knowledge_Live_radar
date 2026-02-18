'use client';

import React, { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { pyramidApi } from '@/lib/api';
import { AISuggestion } from '@/types';
import { RefreshCw, X, Check } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';

interface EvolutionPanelProps {
  pyramidId: string;
  onUpdate?: () => void;
}

const EvolutionPanel: React.FC<EvolutionPanelProps> = ({ pyramidId, onUpdate }) => {
  const t = useTranslations('Evolution');
  const { toast } = useToast();
  const [suggestions, setSuggestions] = useState<AISuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [applyingId, setApplyingId] = useState<string | null>(null);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      const res = await pyramidApi.getSuggestions(pyramidId);
      // Ensure suggestions is an array, handle if API returns wrapped data
      // API response structure might be { success: true, data: [...] } or just [...]
      // Based on typical API wrapper in this project:
      const data = Array.isArray(res) ? res : (Array.isArray(res.data) ? res.data : []);
      setSuggestions(data);
    } catch (error) {
      console.error(error);
      toast({
        title: t('fetch_error'),
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (pyramidId) {
      fetchSuggestions();
    }
  }, [pyramidId]);

  const handleAnalyze = async () => {
    setAnalyzing(true);
    try {
      // mode='all' will run both health and structure analysis
      await pyramidApi.analyze(pyramidId, 'all');
      toast({
        title: t('analysis_complete'),
      });
      fetchSuggestions();
      if (onUpdate) onUpdate();
    } catch (error) {
      console.error(error);
      toast({
        title: t('analysis_error'),
        variant: "destructive",
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleApply = async (suggestionId: string) => {
    if (applyingId) return;
    setApplyingId(suggestionId);
    console.log(`Applying suggestion: ${suggestionId} for pyramid: ${pyramidId}`);
    try {
      await pyramidApi.applySuggestion(pyramidId, suggestionId);
      toast({
        title: t('apply_success'),
      });
      fetchSuggestions();
      if (onUpdate) onUpdate();
    } catch (error: any) {
      console.error('Failed to apply suggestion:', error);
      
      let errorMsg = t('apply_error');
      if (error?.response?.data?.detail) {
        errorMsg += `: ${error.response.data.detail}`;
      } else if (error?.message) {
        errorMsg += `: ${error.message}`;
      }
      
      toast({
        title: errorMsg,
        variant: "destructive",
      });
    } finally {
      setApplyingId(null);
    }
  };

  const handleReject = async (suggestionId: string) => {
    if (applyingId) return;
    try {
      await pyramidApi.rejectSuggestion(pyramidId, suggestionId);
      toast({
        title: t('reject_success'),
      });
      fetchSuggestions();
    } catch (error) {
      console.error(error);
      toast({
        title: t('reject_error'),
        variant: "destructive",
      });
    }
  };

  const getActionLabel = (actionType: string) => {
    try {
      // Try to translate, if key missing it might throw or return key depending on config
      // But we can catch it just in case
      return t(`actions.${actionType}`);
    } catch (error) {
      console.warn(`Translation missing for action: ${actionType}`, error);
      return actionType;
    }
  };

  return (
    <Card className="w-full border-blue-100 shadow-sm">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2 bg-gradient-to-r from-blue-50 to-white rounded-t-lg">
        <div className="flex flex-col space-y-1.5">
          <CardTitle className="text-blue-900">{t('title')}</CardTitle>
          <CardDescription>{t('description')}</CardDescription>
        </div>
        <Button 
          variant="outline" 
          size="sm" 
          onClick={handleAnalyze} 
          disabled={analyzing || !!applyingId}
          className="border-blue-200 text-blue-700 hover:bg-blue-50"
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${analyzing ? 'animate-spin' : ''}`} />
          {analyzing ? t('analyzing') : t('analyze_now')}
        </Button>
      </CardHeader>
      <CardContent className="pt-6">
        {loading ? (
          <div className="flex justify-center p-4">
            <RefreshCw className="h-6 w-6 animate-spin text-gray-400" />
          </div>
        ) : suggestions.length === 0 ? (
          <div className="text-center p-8 text-gray-500 text-sm border border-dashed border-gray-200 rounded-lg bg-gray-50">
            {t('no_suggestions')}
          </div>
        ) : (
          <div className="space-y-4">
            {suggestions.map((suggestion) => (
              <div key={suggestion.id} className="border border-gray-100 rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">
                        {getActionLabel(suggestion.action_type)}
                      </Badge>
                      <span className="text-sm font-semibold text-gray-800">
                        {suggestion.target_name || suggestion.target_id}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 leading-relaxed bg-gray-50 p-3 rounded-md">
                      {suggestion.reason}
                    </p>
                    <div className="flex items-center gap-3 mt-3 text-xs text-gray-400">
                      <span className="flex items-center">
                        <span className="w-2 h-2 rounded-full bg-green-400 mr-1.5"></span>
                        {t('confidence')}: {(suggestion.confidence * 100).toFixed(0)}%
                      </span>
                      <span>•</span>
                      <span>{new Date(suggestion.created_at).toLocaleDateString()}</span>
                    </div>
                  </div>
                  <div className="flex gap-2 self-end sm:self-start min-w-[160px] justify-end">
                    <Button 
                      size="sm" 
                      variant="ghost" 
                      className="text-gray-500 hover:text-red-600 hover:bg-red-50 h-8"
                      onClick={() => handleReject(suggestion.id)}
                      disabled={!!applyingId}
                    >
                      <X className="h-4 w-4 mr-1" />
                      {t('reject')}
                    </Button>
                    <Button 
                      size="sm" 
                      className="bg-blue-600 hover:bg-blue-700 text-white h-8 shadow-sm"
                      onClick={() => handleApply(suggestion.id)}
                      disabled={!!applyingId}
                    >
                      {applyingId === suggestion.id ? (
                        <RefreshCw className="h-4 w-4 mr-1 animate-spin" />
                      ) : (
                        <Check className="h-4 w-4 mr-1" />
                      )}
                      {t('apply')}
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default EvolutionPanel;
