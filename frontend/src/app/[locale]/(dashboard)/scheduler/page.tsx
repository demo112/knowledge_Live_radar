"use client";

import React, { useEffect, useState } from 'react';
import { schedulerApi } from '@/lib/api';
import { ScheduledTask, TaskExecution } from '@/lib/types';
import { Clock, Play, Pause, RotateCw, Activity, CheckCircle, XCircle } from 'lucide-react';

export default function SchedulerPage() {
  const [tasks, setTasks] = useState<ScheduledTask[]>([]);
  const [executions, setExecutions] = useState<TaskExecution[]>([]);

  const fetchData = async () => {
    try {
      const tasksData = await schedulerApi.getAll();
      setTasks(tasksData);
      
      // Fetch recent executions (global)
      const executionsData = await schedulerApi.getExecutions();
      setExecutions(executionsData);
    } catch (error) {
      console.error("Failed to fetch scheduler data", error);
    } finally {
      // setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000); // Auto refresh every 30s
    return () => clearInterval(interval);
  }, []);

  const handleTrigger = async (id: string) => {
    try {
      await schedulerApi.trigger(id);
      fetchData(); // Refresh to show running
    } catch (error) {
      console.error("Failed to trigger task", error);
      alert("触发任务失败");
    }
  };

  const handleToggle = async (task: ScheduledTask) => {
    try {
      if (task.is_active) {
        await schedulerApi.pause(task.id);
      } else {
        await schedulerApi.resume(task.id);
      }
      fetchData();
    } catch (error) {
      console.error("Failed to toggle task", error);
      alert("切换任务状态失败");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
          <Clock className="w-6 h-6 text-blue-600" />
          任务调度 (Scheduler)
        </h1>
        <button 
          onClick={fetchData}
          className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500"
        >
          <RotateCw className="w-5 h-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Task List */}
        <div className="lg:col-span-2 space-y-4">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">定时任务列表</h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-700/50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">任务名</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Cron</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">状态</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">上次运行</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">操作</th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {tasks.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900 dark:text-white">{task.task_name}</div>
                      <div className="text-xs text-gray-500">{task.task_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 font-mono">
                      {task.cron_expression}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        task.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}>
                        {task.is_active ? '活跃' : '暂停'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {task.last_run_at ? new Date(task.last_run_at).toLocaleString() : '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium flex justify-end gap-2">
                      <button 
                        onClick={() => handleToggle(task)}
                        className={`p-1.5 rounded-md ${
                          task.is_active 
                            ? 'text-yellow-600 hover:bg-yellow-50' 
                            : 'text-green-600 hover:bg-green-50'
                        }`}
                        title={task.is_active ? "暂停" : "恢复"}
                      >
                        {task.is_active ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                      </button>
                      <button 
                        onClick={() => handleTrigger(task.id)}
                        className="p-1.5 text-blue-600 hover:bg-blue-50 rounded-md"
                        title="立即运行"
                      >
                        <RotateCw className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Recent Executions */}
        <div className="space-y-4">
          <h2 className="text-lg font-semibold text-gray-800 dark:text-gray-200">最近执行</h2>
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">
            <div className="divide-y divide-gray-200 dark:divide-gray-700 max-h-[600px] overflow-y-auto">
              {executions.length === 0 ? (
                <div className="p-4 text-center text-gray-500 text-sm">无执行记录</div>
              ) : (
                executions.map((exec) => {
                  const task = tasks.find(t => t.id === exec.task_id);
                  return (
                    <div key={exec.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                      <div className="flex justify-between items-start mb-1">
                        <span className="font-medium text-sm text-gray-900 dark:text-white">
                          {task?.task_name || '未知任务'}
                        </span>
                        <span className={`px-1.5 py-0.5 rounded text-[10px] font-medium flex items-center gap-1 ${
                          exec.status === 'success' ? 'bg-green-100 text-green-800' :
                          exec.status === 'failed' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {exec.status === 'success' && <CheckCircle className="w-3 h-3" />}
                          {exec.status === 'failed' && <XCircle className="w-3 h-3" />}
                          {exec.status === 'running' && <Activity className="w-3 h-3 animate-spin" />}
                          {exec.status.toUpperCase()}
                        </span>
                      </div>
                      <div className="text-xs text-gray-500 flex justify-between">
                        <span>{new Date(exec.started_at).toLocaleString()}</span>
                        <span>{exec.duration_seconds ? `${exec.duration_seconds.toFixed(2)}s` : '-'}</span>
                      </div>
                      {exec.error_message && (
                        <div className="mt-2 text-xs text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400 p-2 rounded">
                          {exec.error_message}
                        </div>
                      )}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
