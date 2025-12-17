import React, { useState, useEffect } from 'react';
import { X, Settings, Database, Clock, HelpCircle, ExternalLink, Eye, EyeOff, Download, Upload } from 'lucide-react';
import clsx from 'clsx';
import storage from '../services/storage';

const TABS = [
    { id: 'api', label: 'API 配置', icon: Settings },
    { id: 'data', label: '数据管理', icon: Database },
    { id: 'backup', label: '自动备份', icon: Clock },
];

const BACKUP_INTERVALS = [
    { value: 30, label: '30 分钟' },
    { value: 60, label: '1 小时' },
    { value: 120, label: '2 小时' },
    { value: 1440, label: '24 小时' },
];

export default function SettingsModal({ isOpen, onClose, onConfigChange }) {
    const [activeTab, setActiveTab] = useState('api');
    const [config, setConfig] = useState(storage.DEFAULT_CONFIG);
    const [showApiKey, setShowApiKey] = useState(false);
    const [backupSettings, setBackupSettings] = useState(storage.getBackupSettings());
    const [importing, setImporting] = useState(false);

    useEffect(() => {
        if (isOpen) {
            setConfig(storage.getConfig());
            setBackupSettings(storage.getBackupSettings());
        }
    }, [isOpen]);

    const handleSaveConfig = () => {
        storage.saveConfig(config);
        onConfigChange?.(config);
        onClose();
    };

    const handleExport = () => {
        storage.downloadBackup();
    };

    const handleImport = (e) => {
        const file = e.target.files?.[0];
        if (!file) return;

        setImporting(true);
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const data = JSON.parse(event.target.result);
                const result = storage.importAllData(data);
                if (result.success) {
                    alert('导入成功！页面将刷新以加载新数据。');
                    window.location.reload();
                } else {
                    alert('导入失败：' + result.error);
                }
            } catch (err) {
                alert('文件格式错误：' + err.message);
            }
            setImporting(false);
        };
        reader.readAsText(file);
    };

    const handleBackupSettingsChange = (key, value) => {
        const newSettings = { ...backupSettings, [key]: value };
        setBackupSettings(newSettings);
        storage.saveBackupSettings(newSettings);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

            {/* Modal */}
            <div className="relative bg-background-secondary border border-white/10 rounded-xl w-full max-w-lg mx-4 shadow-2xl overflow-hidden">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/10">
                    <h2 className="text-lg font-semibold text-text-primary">设置</h2>
                    <button onClick={onClose} className="p-1 text-text-muted hover:text-text-primary transition-colors">
                        <X size={20} />
                    </button>
                </div>

                {/* Tabs */}
                <div className="flex border-b border-white/10">
                    {TABS.map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={clsx(
                                "flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors",
                                activeTab === tab.id
                                    ? "text-accent-primary border-b-2 border-accent-primary"
                                    : "text-text-secondary hover:text-text-primary"
                            )}
                        >
                            <tab.icon size={16} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Content */}
                <div className="p-6 max-h-[60vh] overflow-y-auto custom-scrollbar">
                    {/* API Config Tab */}
                    {activeTab === 'api' && (
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1.5">Base URL</label>
                                <input
                                    type="text"
                                    value={config.baseUrl}
                                    onChange={(e) => setConfig({ ...config, baseUrl: e.target.value })}
                                    className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:ring-2 focus:ring-accent-primary/50 outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1.5">Model Name</label>
                                <input
                                    type="text"
                                    value={config.modelName}
                                    onChange={(e) => setConfig({ ...config, modelName: e.target.value })}
                                    className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:ring-2 focus:ring-accent-primary/50 outline-none"
                                />
                            </div>

                            <div>
                                <div className="flex items-center gap-2 mb-1.5">
                                    <label className="text-sm font-medium text-text-secondary">API Key</label>
                                    <div className="group relative">
                                        <HelpCircle size={14} className="text-text-muted cursor-help" />
                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-background-tertiary border border-white/10 rounded-lg text-xs text-text-secondary w-64 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                                            <p className="mb-2">API Key 用于调用智谱 AI 模型服务。</p>
                                            <p>如果没有 API Key，请前往智谱开放平台注册获取。</p>
                                        </div>
                                    </div>
                                    <a
                                        href="https://bigmodel.cn/usercenter/proj-mgmt/apikeys"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-1 text-xs text-accent-primary hover:underline"
                                    >
                                        获取 API Key <ExternalLink size={12} />
                                    </a>
                                </div>
                                <div className="relative">
                                    <input
                                        type={showApiKey ? 'text' : 'password'}
                                        value={config.apiKey}
                                        onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                                        placeholder="请输入您的 API Key"
                                        className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 pr-10 text-sm text-text-primary focus:ring-2 focus:ring-accent-primary/50 outline-none"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowApiKey(!showApiKey)}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1 text-text-muted hover:text-text-primary"
                                    >
                                        {showApiKey ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                            </div>

                            <button
                                onClick={handleSaveConfig}
                                className="w-full mt-4 bg-accent-primary hover:bg-accent-secondary text-white py-2 rounded-lg text-sm font-medium transition-colors"
                            >
                                保存配置
                            </button>
                        </div>
                    )}

                    {/* Data Management Tab */}
                    {activeTab === 'data' && (
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-sm font-medium text-text-primary mb-3">导出数据</h3>
                                <p className="text-xs text-text-muted mb-3">将所有任务历史、配置和统计数据导出为 JSON 文件。</p>
                                <button
                                    onClick={handleExport}
                                    className="flex items-center gap-2 px-4 py-2 bg-background-primary border border-white/10 rounded-lg text-sm text-text-primary hover:bg-white/5 transition-colors"
                                >
                                    <Download size={16} />
                                    导出备份
                                </button>
                            </div>

                            <div className="border-t border-white/10 pt-6">
                                <h3 className="text-sm font-medium text-text-primary mb-3">导入数据</h3>
                                <p className="text-xs text-text-muted mb-3">从 JSON 备份文件恢复数据。这将覆盖当前所有数据。</p>
                                <label className="flex items-center gap-2 px-4 py-2 bg-background-primary border border-white/10 rounded-lg text-sm text-text-primary hover:bg-white/5 transition-colors cursor-pointer">
                                    <Upload size={16} />
                                    {importing ? '导入中...' : '选择文件导入'}
                                    <input
                                        type="file"
                                        accept=".json"
                                        onChange={handleImport}
                                        className="hidden"
                                        disabled={importing}
                                    />
                                </label>
                            </div>

                            <div className="border-t border-white/10 pt-6">
                                <h3 className="text-sm font-medium text-text-primary mb-3">数据统计</h3>
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="bg-background-primary p-3 rounded-lg">
                                        <div className="text-2xl font-bold text-accent-primary">{storage.getHistory().length}</div>
                                        <div className="text-xs text-text-muted">任务记录</div>
                                    </div>
                                    <div className="bg-background-primary p-3 rounded-lg">
                                        <div className="text-2xl font-bold text-accent-primary">{storage.getQueue().length}</div>
                                        <div className="text-xs text-text-muted">队列任务</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Backup Tab */}
                    {activeTab === 'backup' && (
                        <div className="space-y-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <h3 className="text-sm font-medium text-text-primary">自动备份</h3>
                                    <p className="text-xs text-text-muted mt-1">定时自动下载备份文件到默认下载目录</p>
                                </div>
                                <button
                                    onClick={() => handleBackupSettingsChange('enabled', !backupSettings.enabled)}
                                    className={clsx(
                                        "relative w-12 h-6 rounded-full transition-colors",
                                        backupSettings.enabled ? "bg-accent-primary" : "bg-background-tertiary"
                                    )}
                                >
                                    <div
                                        className={clsx(
                                            "absolute top-1 w-4 h-4 bg-white rounded-full transition-transform",
                                            backupSettings.enabled ? "translate-x-7" : "translate-x-1"
                                        )}
                                    />
                                </button>
                            </div>

                            {backupSettings.enabled && (
                                <div>
                                    <label className="block text-sm font-medium text-text-secondary mb-2">备份间隔</label>
                                    <select
                                        value={backupSettings.intervalMinutes}
                                        onChange={(e) => handleBackupSettingsChange('intervalMinutes', Number(e.target.value))}
                                        className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:ring-2 focus:ring-accent-primary/50 outline-none"
                                    >
                                        {BACKUP_INTERVALS.map(interval => (
                                            <option key={interval.value} value={interval.value}>{interval.label}</option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {backupSettings.lastBackupTime && (
                                <div className="bg-background-primary p-3 rounded-lg">
                                    <div className="text-xs text-text-muted">上次备份时间</div>
                                    <div className="text-sm text-text-primary mt-1">
                                        {new Date(backupSettings.lastBackupTime).toLocaleString('zh-CN')}
                                    </div>
                                </div>
                            )}

                            <button
                                onClick={handleExport}
                                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-background-primary border border-white/10 rounded-lg text-sm text-text-primary hover:bg-white/5 transition-colors"
                            >
                                <Download size={16} />
                                立即备份
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
