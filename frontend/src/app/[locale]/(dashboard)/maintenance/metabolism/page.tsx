'use client';

import { useState, useEffect } from 'react';
import { metabolismApi } from '@/lib/api';
import { MetabolismSuggestion, MetabolismRunStats } from '@/types';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

export default function MetabolismPage() {
  const [suggestions, setSuggestions] = useState<MetabolismSuggestion[]>([]);
  const [stats, setStats] = useState<MetabolismRunStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [running, setRunning] = useState(false);
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());

  useEffect(() => {
    fetchSuggestions();
  }, []);

  const fetchSuggestions = async () => {
    setLoading(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = await metabolismApi.getSuggestions() as any;
      if (res && res.items) {
        setSuggestions(res.items);
      } else {
        setSuggestions([]);
      }
    } catch (error) {
      console.error('Failed to fetch suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRun = async () => {
    setRunning(true);
    try {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const res = await metabolismApi.run() as any;
      setStats(res);
      fetchSuggestions(); // Refresh list
    } catch (error) {
      console.error('Failed to run metabolism:', error);
      alert('执行失败，请查看日志');
    } finally {
      setRunning(false);
    }
  };

  const handleCleanup = async () => {
    if (selectedIds.size === 0) return;
    if (!confirm(`确定要永久删除这 ${selectedIds.size} 个项目吗？`)) return;

    try {
      await metabolismApi.cleanup(Array.from(selectedIds));
      setSelectedIds(new Set());
      fetchSuggestions();
      alert('清理完成');
    } catch (error) {
      console.error('Failed to cleanup:', error);
      alert('清理失败');
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === suggestions.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(suggestions.map(s => s.id)));
    }
  };

  return (
    <div className="p-8 space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">内容新陈代谢管理</h1>
          <p className="text-muted-foreground">管理内容生命周期，清理陈旧内容</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={handleRun} disabled={running}>
            {running ? '执行中...' : '立即执行新陈代谢'}
          </Button>
        </div>
      </div>

      {stats && (
        <Card className="bg-green-50 border-green-200">
          <CardContent className="pt-6">
            <div className="flex gap-8">
              <div>
                <div className="text-sm text-gray-500">已处理</div>
                <div className="text-2xl font-bold">{stats.processed}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">转为废弃</div>
                <div className="text-2xl font-bold text-orange-600">{stats.to_deprecated}</div>
              </div>
              <div>
                <div className="text-sm text-gray-500">转为归档</div>
                <div className="text-2xl font-bold text-gray-600">{stats.to_archived}</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <CardTitle>清理建议 ({suggestions.length})</CardTitle>
            {selectedIds.size > 0 && (
              <Button 
                variant="destructive" 
                onClick={handleCleanup}
              >
                清理选中 ({selectedIds.size})
              </Button>
            )}
          </div>
        </CardHeader>
        <CardContent>
          <div className="rounded-md border">
            <table className="w-full text-sm text-left">
              <thead className="bg-muted/50 text-muted-foreground">
                <tr>
                  <th className="p-4 w-12">
                    <input 
                      type="checkbox" 
                      checked={suggestions.length > 0 && selectedIds.size === suggestions.length}
                      onChange={toggleSelectAll}
                      className="cursor-pointer"
                    />
                  </th>
                  <th className="p-4">标题</th>
                  <th className="p-4">分数</th>
                  <th className="p-4">存在时间</th>
                  <th className="p-4">建议原因</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      加载中...
                    </td>
                  </tr>
                ) : suggestions.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="p-8 text-center text-muted-foreground">
                      暂无清理建议
                    </td>
                  </tr>
                ) : (
                  suggestions.map((item) => (
                    <tr key={item.id} className="border-t hover:bg-muted/50">
                      <td className="p-4">
                        <input 
                          type="checkbox" 
                          checked={selectedIds.has(item.id)}
                          onChange={() => toggleSelect(item.id)}
                          className="cursor-pointer"
                        />
                      </td>
                      <td className="p-4 font-medium">{item.title}</td>
                      <td className="p-4">
                        <Badge variant={item.score < 40 ? "destructive" : "secondary"}>
                          {item.score.toFixed(1)}
                        </Badge>
                      </td>
                      <td className="p-4">{item.age_days.toFixed(0)} 天</td>
                      <td className="p-4 text-muted-foreground">{item.reason}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
