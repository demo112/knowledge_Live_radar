'use client';

import { use, useEffect, useState } from 'react';
import { contentApi, evolutionApi } from '@/lib/api';
import { ContentItem } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Sparkles, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export default function ContentDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const unwrappedParams = use(params);
  const contentId = unwrappedParams.id;
  
  const [content, setContent] = useState<ContentItem | null>(null);
  const [nodes, setNodes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [classifying, setClassifying] = useState(false);

  useEffect(() => {
    fetchData();
  }, [contentId]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [contentRes, nodesRes] = await Promise.all([
        contentApi.getById(contentId),
        contentApi.getNodes(contentId)
      ]);
      
      if (contentRes.success) setContent(contentRes.data);
      if (nodesRes.success) setNodes(nodesRes.data);
    } catch (error) {
      console.error('Failed to fetch content data', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClassify = async () => {
    try {
      setClassifying(true);
      const res = await evolutionApi.classifyContent(contentId);
      if (res.success) {
        // Refresh nodes
        const nodesRes = await contentApi.getNodes(contentId);
        if (nodesRes.success) setNodes(nodesRes.data);
        alert(`Classification complete. Linked to ${res.data} nodes.`);
      }
    } catch (error) {
      console.error('Classification failed', error);
      alert('Classification failed');
    } finally {
      setClassifying(false);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (!content) return <div className="p-8">Content not found</div>;

  return (
    <div className="p-8 max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/contents" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <h1 className="text-2xl font-bold truncate flex-1">{content.title}</h1>
        <Button onClick={handleClassify} disabled={classifying}>
          <Sparkles className="mr-2 h-4 w-4" />
          {classifying ? 'Classifying...' : 'AI Auto Classify'}
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Content Details</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-1">Summary</h3>
                <p className="text-muted-foreground">{content.summary || 'No summary available.'}</p>
              </div>
              <div>
                <h3 className="font-semibold mb-1">Concepts</h3>
                <div className="flex flex-wrap gap-2">
                  {content.concepts?.map((c: any, i) => (
                    <Badge key={i} variant="secondary">
                      {typeof c === 'string' ? c : c.name}
                    </Badge>
                  ))}
                </div>
              </div>
              <div>
                 <h3 className="font-semibold mb-1">Source</h3>
                 <a href={content.url} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline break-all">
                   {content.url}
                 </a>
              </div>
            </CardContent>
          </Card>
        </div>

        <div>
          <Card>
            <CardHeader>
              <CardTitle>Linked Nodes ({nodes.length})</CardTitle>
            </CardHeader>
            <CardContent>
              {nodes.length === 0 ? (
                <div className="text-sm text-muted-foreground">No nodes linked yet.</div>
              ) : (
                <div className="space-y-3">
                  {nodes.map(node => (
                    <div key={node.id} className="p-3 border rounded-lg bg-muted/50">
                      <div className="font-medium">{node.name}</div>
                      <div className="flex items-center justify-between mt-2 text-xs text-muted-foreground">
                        <Badge variant="outline">{node.relation_source}</Badge>
                        <span>{(node.relation_confidence * 100).toFixed(0)}%</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
