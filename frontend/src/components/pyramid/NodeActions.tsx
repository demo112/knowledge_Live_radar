import React, { useState } from 'react';
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
          <DialogTitle>拆分节点</DialogTitle>
          <DialogDescription>将此节点拆分为多个子节点。</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
          {subNodes.map((node, index) => (
            <div key={index} className="grid grid-cols-12 gap-2 items-end border-b pb-4">
              <div className="col-span-3">
                <Label>名称</Label>
                <Input value={node.name} onChange={(e) => handleChange(index, 'name', e.target.value)} placeholder="子节点名称" />
              </div>
              <div className="col-span-3">
                 <Label>类型</Label>
                 <Select value={node.node_type} onChange={(e) => handleChange(index, 'node_type', e.target.value)}>
                   <option value="concept">概念</option>
                   <option value="fact">事实</option>
                   <option value="principle">原理</option>
                 </Select>
              </div>
              <div className="col-span-5">
                <Label>内容</Label>
                <Input value={node.content || ''} onChange={(e) => handleChange(index, 'content', e.target.value)} placeholder="内容描述" />
              </div>
              <div className="col-span-1">
                <Button variant="ghost" size="icon" onClick={() => handleRemoveNode(index)} disabled={subNodes.length <= 1}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={handleAddNode} className="w-full">
            <Plus className="h-4 w-4 mr-2" /> 添加子节点
          </Button>
          <div className="flex items-center space-x-2 pt-2">
             <input
               type="checkbox"
               id="deleteOriginal"
               checked={deleteOriginal}
               onChange={(e) => setDeleteOriginal(e.target.checked)}
               className="h-4 w-4 rounded border-gray-300"
             />
             <Label htmlFor="deleteOriginal">拆分后归档原节点</Label>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>取消</Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? '拆分中...' : '确认拆分'}
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
          <DialogTitle>合并节点</DialogTitle>
          <DialogDescription>
            合并 {selectedNodeNames.length} 个节点: {selectedNodeNames.join(', ')}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>合并策略</Label>
            <Select value={strategy} onChange={(e) => setStrategy(e.target.value as any)}>
              <option value="create_new">创建新父节点</option>
              <option value="merge_to_first">合并到第一个选中节点</option>
            </Select>
          </div>
          {strategy === 'create_new' && (
            <>
              <div className="space-y-2">
                <Label>新节点名称</Label>
                <Input value={targetName} onChange={(e) => setTargetName(e.target.value)} placeholder="合并后的节点名称" />
              </div>
              <div className="space-y-2">
                <Label>内容 (可选)</Label>
                <Input value={targetContent} onChange={(e) => setTargetContent(e.target.value)} placeholder="合并后的内容摘要" />
              </div>
            </>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>取消</Button>
          <Button onClick={handleSubmit} disabled={isLoading || (strategy === 'create_new' && !targetName)}>
            {isLoading ? '合并中...' : '确认合并'}
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
  const [targetNodeId, setTargetNodeId] = useState('');
  const [relationType, setRelationType] = useState('related');

  const handleSubmit = () => {
    onConfirm({ target_node_id: targetNodeId, relation_type: relationType });
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>关联节点</DialogTitle>
          <DialogDescription>创建对另一个节点的引用。</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>目标节点 ID</Label>
            <Input value={targetNodeId} onChange={(e) => setTargetNodeId(e.target.value)} placeholder="目标节点 UUID" />
            <p className="text-xs text-gray-500">当前仅支持直接通过 ID 关联。</p>
          </div>
          <div className="space-y-2">
            <Label>关系类型</Label>
            <Select value={relationType} onChange={(e) => setRelationType(e.target.value)}>
              <option value="related">相关</option>
              <option value="prerequisite">前置</option>
              <option value="part_of">部分</option>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>取消</Button>
          <Button onClick={handleSubmit} disabled={isLoading || !targetNodeId}>
            {isLoading ? '关联中...' : '确认关联'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
