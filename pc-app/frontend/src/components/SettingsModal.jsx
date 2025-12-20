import React, { useState, useEffect } from 'react';
import { X, Settings, Database, Clock, HelpCircle, ExternalLink, Eye, EyeOff, Download, Upload, Globe } from 'lucide-react';
import clsx from 'clsx';
import storage from '../services/storage';
import { useLanguage, LOCALES } from '../i18n/i18n.jsx';

const BACKUP_INTERVALS = [
    { value: 30, label: '30' },
    { value: 60, label: '60' },
    { value: 120, label: '120' },
    { value: 1440, label: '1440' },
];

export default function SettingsModal({ isOpen, onClose, onConfigChange }) {
    const { t, locale, setLocale } = useLanguage();

    const [activeTab, setActiveTab] = useState('api');
    const [config, setConfig] = useState(storage.DEFAULT_CONFIG);
    const [showApiKey, setShowApiKey] = useState(false);
    const [backupSettings, setBackupSettings] = useState(storage.getBackupSettings());
    const [importing, setImporting] = useState(false);

    const TABS = [
        { id: 'api', label: t('settings.tabs.api'), icon: Settings },
        { id: 'data', label: t('settings.tabs.data'), icon: Database },
        { id: 'backup', label: t('settings.tabs.backup'), icon: Clock },
        { id: 'language', label: t('settings.tabs.language'), icon: Globe },
    ];

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
                    alert(t('settings.data.importSuccess'));
                    window.location.reload();
                } else {
                    alert(t('settings.data.importFailed') + result.error);
                }
            } catch (err) {
                alert(t('settings.data.fileFormatError') + err.message);
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
                    <h2 className="text-lg font-semibold text-text-primary">{t('settings.title')}</h2>
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
                                <label className="block text-sm font-medium text-text-secondary mb-1.5">{t('settings.api.baseUrl')}</label>
                                <input
                                    type="text"
                                    value={config.baseUrl}
                                    onChange={(e) => setConfig({ ...config, baseUrl: e.target.value })}
                                    className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:ring-2 focus:ring-accent-primary/50 outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-text-secondary mb-1.5">{t('settings.api.modelName')}</label>
                                <input
                                    type="text"
                                    value={config.modelName}
                                    onChange={(e) => setConfig({ ...config, modelName: e.target.value })}
                                    className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:ring-2 focus:ring-accent-primary/50 outline-none"
                                />
                            </div>

                            <div>
                                <div className="flex items-center gap-2 mb-1.5">
                                    <label className="text-sm font-medium text-text-secondary">{t('settings.api.apiKey')}</label>
                                    <div className="group relative">
                                        <HelpCircle size={14} className="text-text-muted cursor-help" />
                                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-2 bg-background-tertiary border border-white/10 rounded-lg text-xs text-text-secondary w-64 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-10">
                                            <p className="mb-2">{t('settings.api.apiKeyHelp')}</p>
                                            <p>{t('settings.api.apiKeyHelpExtra')}</p>
                                        </div>
                                    </div>
                                    <a
                                        href="https://bigmodel.cn/usercenter/proj-mgmt/apikeys"
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        className="flex items-center gap-1 text-xs text-accent-primary hover:underline"
                                    >
                                        {t('settings.api.getApiKey')} <ExternalLink size={12} />
                                    </a>
                                </div>
                                <div className="relative">
                                    <input
                                        type={showApiKey ? 'text' : 'password'}
                                        value={config.apiKey}
                                        onChange={(e) => setConfig({ ...config, apiKey: e.target.value })}
                                        placeholder={t('settings.api.placeholder')}
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
                                {t('settings.api.save')}
                            </button>
                        </div>
                    )}

                    {/* Data Management Tab */}
                    {activeTab === 'data' && (
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-sm font-medium text-text-primary mb-3">{t('settings.data.exportTitle')}</h3>
                                <p className="text-xs text-text-muted mb-3">{t('settings.data.exportDesc')}</p>
                                <button
                                    onClick={handleExport}
                                    className="flex items-center gap-2 px-4 py-2 bg-background-primary border border-white/10 rounded-lg text-sm text-text-primary hover:bg-white/5 transition-colors"
                                >
                                    <Download size={16} />
                                    {t('settings.data.exportButton')}
                                </button>
                            </div>

                            <div className="border-t border-white/10 pt-6">
                                <h3 className="text-sm font-medium text-text-primary mb-3">{t('settings.data.importTitle')}</h3>
                                <p className="text-xs text-text-muted mb-3">{t('settings.data.importDesc')}</p>
                                <label className="flex items-center gap-2 px-4 py-2 bg-background-primary border border-white/10 rounded-lg text-sm text-text-primary hover:bg-white/5 transition-colors cursor-pointer">
                                    <Upload size={16} />
                                    {importing ? t('settings.data.importing') : t('settings.data.importButton')}
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
                                <h3 className="text-sm font-medium text-text-primary mb-3">{t('settings.data.statsTitle')}</h3>
                                <div className="grid grid-cols-2 gap-3">
                                    <div className="bg-background-primary p-3 rounded-lg">
                                        <div className="text-2xl font-bold text-accent-primary">{storage.getHistory().length}</div>
                                        <div className="text-xs text-text-muted">{t('settings.data.taskRecords')}</div>
                                    </div>
                                    <div className="bg-background-primary p-3 rounded-lg">
                                        <div className="text-2xl font-bold text-accent-primary">{storage.getQueue().length}</div>
                                        <div className="text-xs text-text-muted">{t('settings.data.queueTasks')}</div>
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
                                    <h3 className="text-sm font-medium text-text-primary">{t('settings.backup.autoBackup')}</h3>
                                    <p className="text-xs text-text-muted mt-1">{t('settings.backup.autoBackupDesc')}</p>
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
                                    <label className="block text-sm font-medium text-text-secondary mb-2">{t('settings.backup.interval')}</label>
                                    <select
                                        value={backupSettings.intervalMinutes}
                                        onChange={(e) => handleBackupSettingsChange('intervalMinutes', Number(e.target.value))}
                                        className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm text-text-primary focus:ring-2 focus:ring-accent-primary/50 outline-none"
                                    >
                                        {BACKUP_INTERVALS.map(interval => (
                                            <option key={interval.value} value={interval.value}>
                                                {t(`settings.backup.intervals.${interval.value}`)}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            )}

                            {backupSettings.lastBackupTime && (
                                <div className="bg-background-primary p-3 rounded-lg">
                                    <div className="text-xs text-text-muted">{t('settings.backup.lastBackupTime')}</div>
                                    <div className="text-sm text-text-primary mt-1">
                                        {new Date(backupSettings.lastBackupTime).toLocaleString(locale === 'zh-CN' ? 'zh-CN' : 'en-US')}
                                    </div>
                                </div>
                            )}

                            <button
                                onClick={handleExport}
                                className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-background-primary border border-white/10 rounded-lg text-sm text-text-primary hover:bg-white/5 transition-colors"
                            >
                                <Download size={16} />
                                {t('settings.backup.backupNow')}
                            </button>
                        </div>
                    )}

                    {/* Language Tab */}
                    {activeTab === 'language' && (
                        <div className="space-y-6">
                            <div>
                                <h3 className="text-sm font-medium text-text-primary mb-2">{t('settings.language.title')}</h3>
                                <p className="text-xs text-text-muted mb-4">{t('settings.language.desc')}</p>

                                <div className="space-y-2">
                                    {Object.entries(LOCALES).map(([key, { name }]) => (
                                        <button
                                            key={key}
                                            onClick={() => setLocale(key)}
                                            className={clsx(
                                                "w-full flex items-center justify-between p-3 rounded-lg border transition-all",
                                                locale === key
                                                    ? "bg-accent-primary/10 border-accent-primary text-text-primary"
                                                    : "bg-background-primary border-white/10 text-text-secondary hover:border-white/20"
                                            )}
                                        >
                                            <span className="font-medium">{name}</span>
                                            {locale === key && (
                                                <span className="text-accent-primary text-xs">✓</span>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
