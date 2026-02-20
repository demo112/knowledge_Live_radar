'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { pyramidApi } from '@/lib/api';
import { Pyramid } from '@/types';
import { Loader2 } from 'lucide-react';

interface DiscoverySetupDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onStart: (pyramidId: string | undefined) => void;
}

export default function DiscoverySetupDialog({
  open,
  onOpenChange,
  onStart
}: DiscoverySetupDialogProps) {
  const t = useTranslations('Sources.discovery');
  const tCommon = useTranslations('Common');
  
  const [pyramids, setPyramids] = useState<Pyramid[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPyramidId, setSelectedPyramidId] = useState<string>('');

  useEffect(() => {
    const fetchPyramids = async () => {
      setLoading(true);
      try {
        const response = await pyramidApi.getAll();
        if (response.success) {
          setPyramids(response.data.items);
          if (response.data.items.length > 0 && !selectedPyramidId) {
            setSelectedPyramidId(response.data.items[0].id);
          }
        }
      } catch (error) {
        console.error('Failed to fetch pyramids:', error);
      } finally {
        setLoading(false);
      }
    };

    if (open) {
      fetchPyramids();
    }
  }, [open, selectedPyramidId]);

  const handleStart = () => {
    if (!selectedPyramidId) return;
    onStart(selectedPyramidId);
    onOpenChange(false);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>{t('setup_title')}</DialogTitle>
          <DialogDescription>
            {t('setup_description')}
          </DialogDescription>
        </DialogHeader>
        
        <div className="grid gap-4 py-4">
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="pyramid" className="text-right">
              {t('context_pyramid')}
            </Label>
            <div className="col-span-3">
              <Select
                value={selectedPyramidId}
                onValueChange={setSelectedPyramidId}
                disabled={loading}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder={t('select_pyramid_placeholder')} />
                </SelectTrigger>
                <SelectContent>
                  {pyramids.map((pyramid) => (
                    <SelectItem key={pyramid.id} value={pyramid.id}>
                      {pyramid.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>
            {tCommon('cancel')}
          </Button>
          <Button onClick={handleStart} disabled={loading || !selectedPyramidId}>
            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            {t('start_discovery')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
