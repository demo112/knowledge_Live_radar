import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Folder, FileText } from 'lucide-react';
import { useTranslations } from 'next-intl';

export interface PyramidNodeStructure {
  name: string;
  description?: string;
  children?: PyramidNodeStructure[];
}

interface PyramidPreviewProps {
  structure: PyramidNodeStructure;
  className?: string;
}

const TreeNode = ({ node, level = 0 }: { node: PyramidNodeStructure; level?: number }) => {
  return (
    <div className="ml-4">
      <div className="flex items-center gap-2 py-1">
        {node.children && node.children.length > 0 ? (
          <Folder className="h-4 w-4 text-blue-500" />
        ) : (
          <FileText className="h-4 w-4 text-slate-400" />
        )}
        <span className="font-medium text-sm text-slate-800">{node.name}</span>
        {node.description && (
          <span className="text-xs text-slate-500 truncate max-w-[300px]">
            - {node.description}
          </span>
        )}
      </div>
      {node.children && (
        <div className="border-l border-slate-200 ml-2 pl-2">
          {node.children.map((child, idx) => (
            <TreeNode key={idx} node={child} level={level + 1} />
          ))}
        </div>
      )}
    </div>
  );
};

export function PyramidPreview({ structure, className }: PyramidPreviewProps) {
  const t = useTranslations('Components.PyramidPreview');

  return (
    <Card className={className}>
      <CardContent className="pt-6">
        <h3 className="text-lg font-semibold mb-4">{t('title')}</h3>
        <div className="bg-white rounded-md border p-4 overflow-auto max-h-[400px]">
          <TreeNode node={structure} />
        </div>
      </CardContent>
    </Card>
  );
}
