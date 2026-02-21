'use client';

import React, { useState } from 'react';
import { intentApi, IntentResponse, Action } from '@/lib/api/intent';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Loader2, ArrowRight } from 'lucide-react';

export default function IntentInput() {
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<IntentResponse | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    try {
      const response = await intentApi.process(input);
      if (response.success) {
        setResult(response.data);
      }
    } catch (error) {
      console.error('Failed to process intent:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async (action: Action) => {
    // TODO: Implement execution logic (Task 5.2 extension)
    console.log('Executing action:', action);
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-4">
      <form onSubmit={handleSubmit} className="flex gap-2 mb-6">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="What do you want to learn or research?"
          className="flex-1"
          disabled={loading}
        />
        <Button type="submit" disabled={loading}>
          {loading ? <Loader2 className="animate-spin" /> : <ArrowRight />}
        </Button>
      </form>

      {result && (
        <div className="bg-white p-6 rounded-lg shadow border">
          <div className="mb-4">
            <h3 className="font-semibold text-lg text-primary mb-1">
              Intent: {result.parsed_intent.intent_type.toUpperCase()}
            </h3>
            <p className="text-gray-600">
              Topic: <span className="font-medium">{result.parsed_intent.primary_topic}</span>
            </p>
            {result.parsed_intent.goal && (
              <p className="text-gray-500 text-sm italic mt-1">Goal: {result.parsed_intent.goal}</p>
            )}
          </div>

          <div className="space-y-3">
            <h4 className="font-medium text-gray-700 border-b pb-2">Suggested Actions</h4>
            {result.suggested_actions.map((action, idx) => (
              <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded border hover:bg-gray-100 transition-colors">
                <div>
                  <div className="font-medium text-sm text-gray-800">{action.description}</div>
                  <div className="text-xs text-gray-500 mt-1">Type: {action.type}</div>
                </div>
                <Button size="sm" variant="outline" onClick={() => handleExecute(action)}>
                  Execute
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
