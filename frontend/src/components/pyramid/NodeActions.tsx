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
          <DialogTitle>Split Node</DialogTitle>
          <DialogDescription>Split this node into multiple sub-nodes.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 max-h-[60vh] overflow-y-auto pr-2">
          {subNodes.map((node, index) => (
            <div key={index} className="grid grid-cols-12 gap-2 items-end border-b pb-4">
              <div className="col-span-3">
                <Label>Name</Label>
                <Input value={node.name} onChange={(e) => handleChange(index, 'name', e.target.value)} placeholder="Sub-node name" />
              </div>
              <div className="col-span-3">
                 <Label>Type</Label>
                 <Select value={node.node_type} onChange={(e) => handleChange(index, 'node_type', e.target.value)}>
                   <option value="concept">Concept</option>
                   <option value="fact">Fact</option>
                   <option value="principle">Principle</option>
                 </Select>
              </div>
              <div className="col-span-5">
                <Label>Content</Label>
                <Input value={node.content || ''} onChange={(e) => handleChange(index, 'content', e.target.value)} placeholder="Content" />
              </div>
              <div className="col-span-1">
                <Button variant="ghost" size="icon" onClick={() => handleRemoveNode(index)} disabled={subNodes.length <= 1}>
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
          <Button variant="outline" size="sm" onClick={handleAddNode} className="w-full">
            <Plus className="h-4 w-4 mr-2" /> Add Sub-node
          </Button>
          <div className="flex items-center space-x-2 pt-2">
             <input
               type="checkbox"
               id="deleteOriginal"
               checked={deleteOriginal}
               onChange={(e) => setDeleteOriginal(e.target.checked)}
               className="h-4 w-4 rounded border-gray-300"
             />
             <Label htmlFor="deleteOriginal">Archive original node after split</Label>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? 'Splitting...' : 'Confirm Split'}
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
          <DialogTitle>Merge Nodes</DialogTitle>
          <DialogDescription>
            Merging {selectedNodeNames.length} nodes: {selectedNodeNames.join(', ')}
          </DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Merge Strategy</Label>
            <Select value={strategy} onChange={(e) => setStrategy(e.target.value as any)}>
              <option value="create_new">Create New Parent Node</option>
              <option value="merge_to_first">Merge into First Selected</option>
            </Select>
          </div>
          {strategy === 'create_new' && (
            <>
              <div className="space-y-2">
                <Label>New Node Name</Label>
                <Input value={targetName} onChange={(e) => setTargetName(e.target.value)} placeholder="Merged Node Name" />
              </div>
              <div className="space-y-2">
                <Label>Content (Optional)</Label>
                <Input value={targetContent} onChange={(e) => setTargetContent(e.target.value)} placeholder="Merged Content Summary" />
              </div>
            </>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={isLoading || (strategy === 'create_new' && !targetName)}>
            {isLoading ? 'Merging...' : 'Confirm Merge'}
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
          <DialogTitle>Link Node</DialogTitle>
          <DialogDescription>Create a cross-reference to another node.</DialogDescription>
        </DialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label>Target Node ID</Label>
            <Input value={targetNodeId} onChange={(e) => setTargetNodeId(e.target.value)} placeholder="UUID of target node" />
            <p className="text-xs text-gray-500">Currently only supports linking by ID directly.</p>
          </div>
          <div className="space-y-2">
            <Label>Relation Type</Label>
            <Select value={relationType} onChange={(e) => setRelationType(e.target.value)}>
              <option value="related">Related</option>
              <option value="supports">Supports</option>
              <option value="contradicts">Contradicts</option>
              <option value="expands">Expands</option>
            </Select>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Cancel</Button>
          <Button onClick={handleSubmit} disabled={isLoading || !targetNodeId}>
            {isLoading ? 'Linking...' : 'Confirm Link'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
