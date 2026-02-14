'use client';

import React, { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter, DialogDescription } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { NodeCreate, SplitRequest, MergeRequest, LinkRequest } from '@/types';
import { Plus, Trash2 } from 'lucide-react';

// --- Split Node Dialog ---

interface SplitNodeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (data: SplitRequest) => void;
  isLoading?: boolean;
}

export const SplitNodeDialog: React.FC<SplitNodeDialogProps> = ({ open, onOpenChange, onConfirm, isLoading }) => {
  const t = useTranslations('Pyramid.Detail.NodeActions');
  const [subNodes, setSubNodes] = useState<NodeCreate[]>([
    { name: '', content: '', node_type: 'concept' },
    { name: '', content: '', node_type: 'concept' }
  ]);
  const [deleteOriginal, setDeleteOriginal] = useState(false);

  const handleAddNode = () => {
    setSubNodes([...subNodes, { name: '', content: '', node_type: 'concept' }]);
  };

  const handleRemoveNode = (index: number) => {
    setSubNodes(subNodes.filter((_, i) => i !== index));
  };

  const handleChange = (index: number, field: keyof NodeCreate, value: string) => {
    const newNodes = [...subNodes];
    newNodes[index] = { ...newNodes[index], [field]: value };
    setSubNodes(newNodes);
  };

  const handleSubmit = () => {
    onConfirm({ sub_nodes: subNodes, delete_original: deleteOriginal });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{t('Split.title')}</DialogTitle>
          <DialogDescription>{t('Split.description')}</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
          {subNodes.map((node, index) => (
            <div key={index} className="grid grid-cols-12 gap-2 items-end border-b pb-4">
              <div className="col-span-3">
                <Label>{t('Split.name_label')}</Label>
                <Input value={node.name} onChange={(e) => handleChange(index, 'name', e.target.value)} placeholder={t('Split.name_placeholder')} />
              </div>
              <div className="col-span-3">
                 <Label>{t('Split.type_label')}</Label>
                 <Select value={node.node_type} onChange={(e) => handleChange(index, 'node_type', e.target.value)}>
                   <option value="concept">{t('Split.types.concept')}</option>
                   <option value="fact">{t('Split.types.fact')}</option>
                   <option value="principle">{t('Split.types.principle')}</option>
                 </Select>
              </div>
              <div className="col-span-5">
                <Label>{t('Split.content_label')}</Label>
                <Input value={node.content || ''} onChange={(e) => handleChange(index, 'content', e.target.value)} placeholder={t('Split.content_placeholder')} />
              </div>
              <div className="col-span-1">
                <Button variant="ghost" size="icon" onClick={() => handleRemoveNode(index)} disabled={subNodes.length <= 1}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={handleAddNode} className="w-full">
            <Plus className="h-4 w-4 mr-2" /> {t('Split.add_sub_node')}
          </Button>
          <div className="flex items-center space-x-2 pt-2">
             <input
               type="checkbox"
               id="deleteOriginal"
               checked={deleteOriginal}
               onChange={(e) => setDeleteOriginal(e.target.checked)}
               className="h-4 w-4 rounded border-gray-300"
             />
             <Label htmlFor="deleteOriginal">{t('Split.archive_original')}</Label>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>{t('common.cancel')}</Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? t('Split.processing') : t('Split.confirm')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// --- Merge Nodes Dialog ---

interface MergeNodesDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  selectedNodeNames: string[];
  onConfirm: (data: MergeRequest) => void;
  isLoading?: boolean;
}

export const MergeNodesDialog: React.FC<MergeNodesDialogProps> = ({ open, onOpenChange, selectedNodeNames, onConfirm, isLoading }) => {
  const t = useTranslations('Pyramid.Detail.NodeActions');
  const [targetName, setTargetName] = useState('');
  const [targetContent, setTargetContent] = useState('');
  const [strategy, setStrategy] = useState<'create_new' | 'merge_to_first'>('create_new');

  const handleSubmit = () => {
    // Note: source_node_ids will be handled by the parent component
    onConfirm({
      source_node_ids: [], // Placeholder, parent fills this
      target_node_name: targetName,
      target_node_content: targetContent,
      strategy
    });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t('Merge.title')}</DialogTitle>
          <DialogDescription>
            {t('Merge.description', { count: selectedNodeNames.length, names: selectedNodeNames.join(', ') })}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>{t('Merge.strategy_label')}</Label>
            <Select value={strategy} onChange={(e) => setStrategy(e.target.value as 'create_new' | 'merge_to_first')}>
              <option value="create_new">{t('Merge.strategies.create_new')}</option>
              <option value="merge_to_first">{t('Merge.strategies.merge_to_first')}</option>
            </Select>
          </div>
          {strategy === 'create_new' && (
            <>
              <div className="space-y-2">
                <Label>{t('Merge.new_name_label')}</Label>
                <Input value={targetName} onChange={(e) => setTargetName(e.target.value)} placeholder={t('Merge.new_name_placeholder')} />
              </div>
              <div className="space-y-2">
                <Label>{t('Merge.content_label')}</Label>
                <Input value={targetContent} onChange={(e) => setTargetContent(e.target.value)} placeholder={t('Merge.content_placeholder')} />
              </div>
            </>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>{t('common.cancel')}</Button>
          <Button onClick={handleSubmit} disabled={isLoading || (strategy === 'create_new' && !targetName)}>
            {isLoading ? t('Merge.processing') : t('Merge.confirm')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};

// --- Link Node Dialog ---

interface LinkNodeDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (data: LinkRequest) => void;
  isLoading?: boolean;
}

export const LinkNodeDialog: React.FC<LinkNodeDialogProps> = ({ open, onOpenChange, onConfirm, isLoading }) => {
  const t = useTranslations('Pyramid.Detail.NodeActions');
  const [targetNodeId, setTargetNodeId] = useState('');
  const [relationType, setRelationType] = useState('related');

  const handleSubmit = () => {
    onConfirm({ target_node_id: targetNodeId, relation_type: relationType });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{t('Link.title')}</DialogTitle>
          <DialogDescription>{t('Link.description')}</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>{t('Link.target_id_label')}</Label>
            <Input value={targetNodeId} onChange={(e) => setTargetNodeId(e.target.value)} placeholder={t('Link.target_id_placeholder')} />
            <p className="text-xs text-gray-500">{t('Link.target_id_hint')}</p>
          </div>
          <div className="space-y-2">
            <Label>{t('Link.relation_label')}</Label>
            <Select value={relationType} onChange={(e) => setRelationType(e.target.value)}>
              <option value="related">{t('Link.relations.related')}</option>
              <option value="prerequisite">{t('Link.relations.prerequisite')}</option>
              <option value="part_of">{t('Link.relations.part_of')}</option>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>{t('common.cancel')}</Button>
          <Button onClick={handleSubmit} disabled={isLoading || !targetNodeId}>
            {isLoading ? t('Link.processing') : t('Link.confirm')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
