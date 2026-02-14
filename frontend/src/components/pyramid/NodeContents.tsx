'use client';

import React, { useEffect, useState } from 'react';
import { ContentWithRelation } from '@/types';
import { nodeApi } from '@/lib/api';
import { Trash2, Link as LinkIcon, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface NodeContentsProps {
  nodeId: string;
}

export function NodeContents({ nodeId }: NodeContentsProps) {
  const [contents, setContents] = useState<ContentWithRelation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadContents = async () => {
      try {
        setLoading(true);
        const res = await nodeApi.getContents(nodeId);
        if (res.success) {
          setContents(res.data);
        }
      } catch (error) {
        console.error('Failed to load contents', error);
      } finally {
        setLoading(false);
      }
    };
    loadContents();
  }, [nodeId]);

  const handleUnlink = async (contentId: string) => {
    if (!confirm('Are you sure you want to unlink this content?')) return;
    try {
      await nodeApi.unlinkContent(nodeId, contentId);
      setContents(prev => prev.filter(c => c.id !== contentId));
    } catch (error) {
      console.error('Failed to unlink content', error);
    }
  };

  if (loading) return <div className="p-4 text-center text-muted-foreground">Loading contents...</div>;

  return (
    <Card className="mt-6">
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <LinkIcon className="h-5 w-5" />
          Associated Content ({contents.length})
        </CardTitle>
      </CardHeader>
      <CardContent>
        {contents.length === 0 ? (
          <div className="text-muted-foreground text-sm">No content associated with this node.</div>
        ) : (
          <div className="space-y-4">
            {contents.map(content => (
              <div key={content.id} className="flex items-start justify-between p-4 border rounded-lg">
                <div className="space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <a href={content.url} target="_blank" rel="noopener noreferrer" className="font-medium hover:underline flex items-center gap-1 text-primary">
                      {content.title}
                      <ExternalLink className="h-3 w-3" />
                    </a>
                    <div className="flex items-center gap-2">
                      <Badge variant={content.relation_source === 'ai_auto' ? 'secondary' : 'outline'}>
                        {content.relation_source === 'ai_auto' ? 'AI Auto' : 'Manual'}
                      </Badge>
                      {content.relation_source === 'ai_auto' && (
                        <span className="text-xs text-muted-foreground">
                          {(content.relation_confidence * 100).toFixed(0)}% match
                        </span>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-muted-foreground line-clamp-2">{content.summary || 'No summary available.'}</p>
                  {content.concepts && content.concepts.length > 0 && (
                    <div className="flex gap-1 mt-1 flex-wrap">
                      {content.concepts.map((c: unknown, i) => (
                        <span key={i} className="text-xs bg-muted px-1.5 py-0.5 rounded">
                          {typeof c === 'string' ? c : (c as { name: string }).name}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <Button variant="ghost" size="icon" onClick={() => handleUnlink(content.id)} className="text-destructive hover:text-destructive/90 shrink-0 ml-2">
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
