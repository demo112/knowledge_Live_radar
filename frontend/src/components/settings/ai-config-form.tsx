import React, { useState, useEffect } from 'react';
import { configApi } from '@/lib/api';
import { Save, Activity, RefreshCw, Eye, EyeOff, AlertTriangle, CheckCircle } from 'lucide-react';

export default function AIConfigForm() {
  const [configs, setConfigs] = useState<Record<string, unknown>>({
    'ai.api_key': '',
    'ai.base_url': 'https://api.siliconflow.cn/v1',
    'ai.model': 'Qwen/Qwen2.5-7B-Instruct',
    'ai.temperature': 0.7,
    'ai.max_retries': 3,
    'ai.enabled': false
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [showKey, setShowKey] = useState(false);
  const [testResult, setTestResult] = useState<{ success: boolean; message: string; latency_ms?: number } | null>(null);

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const data = await configApi.getAll();
      setConfigs((prev) => ({ ...prev, ...data }));
    } catch (error) {
      console.error("Failed to load configs", error);
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (key: string, value: unknown) => {
    setConfigs((prev) => ({ ...prev, [key]: value }));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Save all fields
      for (const [key, value] of Object.entries(configs)) {
        // Skip api key if it is masked (starts with sk- and contains ***)
        if (key === 'ai.api_key' && typeof value === 'string' && value.includes('***')) {
          continue;
        }
        await configApi.update(key, value);
      }
      
      // Reload to get canonical values (and re-masked key)
      await loadConfigs();
      alert('配置已保存');
    } catch (error) {
      console.error("Failed to save configs", error);
      alert('保存失败');
    } finally {
      setSaving(false);
    }
  };

  const handleTestConnection = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const result = await configApi.testAIConnection();
      setTestResult(result);
    } catch (error) {
      console.error("Test failed", error);
      setTestResult({ success: false, message: '连接测试失败: ' + (error instanceof Error ? error.message : String(error)) });
    } finally {
      setTesting(false);
    }
  };

  if (loading) {
    return <div className="p-8 text-center text-gray-500">加载配置中...</div>;
  }

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 space-y-6">
      <div className="flex justify-between items-center border-b pb-4">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
          <Activity className="w-5 h-5 text-blue-500" />
          AI 模型配置
        </h2>
        <div className="flex items-center gap-2">
           <label className="flex items-center cursor-pointer relative">
             <input 
               type="checkbox" 
               className="sr-only peer"
               checked={Boolean(configs['ai.enabled'])}
               onChange={(e) => handleChange('ai.enabled', e.target.checked)}
             />
             <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
             <span className="ml-3 text-sm font-medium text-gray-900 dark:text-gray-300">启用 AI 功能</span>
           </label>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {/* Base URL */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            API Base URL
          </label>
          <input
            type="text"
            value={(configs['ai.base_url'] as string) || ''}
            onChange={(e) => handleChange('ai.base_url', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="https://api.siliconflow.cn/v1"
          />
          <p className="mt-1 text-xs text-gray-500">兼容 OpenAI 接口的服务地址</p>
        </div>

        {/* API Key */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            API Key
          </label>
          <div className="relative">
            <input
              type={showKey ? "text" : "password"}
              value={(configs['ai.api_key'] as string) || ''}
              onChange={(e) => handleChange('ai.api_key', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white pr-10"
              placeholder="sk-..."
            />
            <button
              type="button"
              onClick={() => setShowKey(!showKey)}
              className="absolute inset-y-0 right-0 px-3 flex items-center text-gray-500 hover:text-gray-700"
            >
              {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
            </button>
          </div>
          <p className="mt-1 text-xs text-gray-500">如显示为 *** 则表示已脱敏，无需修改。留空则禁用 AI。</p>
        </div>

        {/* Model */}
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            模型名称 (Model)
          </label>
          <input
            type="text"
            value={(configs['ai.model'] as string) || ''}
            onChange={(e) => handleChange('ai.model', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            placeholder="Qwen/Qwen2.5-7B-Instruct"
          />
        </div>

        {/* Parameters Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Temperature */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              温度 (Temperature): {configs['ai.temperature'] as number}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={(configs['ai.temperature'] as number) || 0.7}
              onChange={(e) => handleChange('ai.temperature', parseFloat(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>精确 (0.0)</span>
              <span>均衡 (1.0)</span>
              <span>创意 (2.0)</span>
            </div>
          </div>

          {/* Max Retries */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              最大重试次数
            </label>
            <input
              type="number"
              min="0"
              max="10"
              value={(configs['ai.max_retries'] as number) || 3}
              onChange={(e) => handleChange('ai.max_retries', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
            />
          </div>
        </div>
      </div>

      {/* Test Result Area */}
      {testResult && (
        <div className={`p-4 rounded-md flex items-start gap-3 ${testResult.success ? 'bg-green-50 text-green-700 border border-green-200' : 'bg-red-50 text-red-700 border border-red-200'}`}>
          {testResult.success ? <CheckCircle className="w-5 h-5 mt-0.5" /> : <AlertTriangle className="w-5 h-5 mt-0.5" />}
          <div>
            <p className="font-medium">{testResult.success ? '连接成功' : '连接失败'}</p>
            <p className="text-sm mt-1">{testResult.message}</p>
            {testResult.latency_ms && (
              <p className="text-xs mt-1 opacity-80">延迟: {testResult.latency_ms.toFixed(0)}ms</p>
            )}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-4 pt-4 border-t">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {saving ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
          保存配置
        </button>

        <button
          onClick={handleTestConnection}
          disabled={testing || !configs['ai.enabled']}
          className="flex items-center gap-2 px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 disabled:opacity-50 transition-colors dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600"
        >
          {testing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
          测试连接
        </button>
      </div>
    </div>
  );
}
