// LocalStorage Service for AI Phone
// Handles all persistent data storage in browser localStorage

const STORAGE_KEYS = {
    CONFIG: 'aiphone_config',
    HISTORY: 'aiphone_history',
    QUEUE: 'aiphone_queue',
    STATS: 'aiphone_stats',
    BACKUP_SETTINGS: 'aiphone_backup_settings',
    LAST_BACKUP: 'aiphone_last_backup',
    TRASH: 'aiphone_trash', // Trash bin for deleted items
    SHORTCUTS: 'aiphone_shortcuts', // Quick command shortcuts
    PREFERENCES: 'aiphone_preferences', // User preferences (page size, etc.)
};

// Default configuration
const DEFAULT_CONFIG = {
    baseUrl: 'https://open.bigmodel.cn/api/paas/v4',
    modelName: 'autoglm-phone',
    apiKey: '',
};

const DEFAULT_BACKUP_SETTINGS = {
    enabled: false,
    intervalMinutes: 60, // 1 hour default
    lastBackupTime: null,
};

const TRASH_RETENTION_DAYS = 30;

const DEFAULT_PREFERENCES = {
    shortcutsPageSize: 10,
    shortcutsCategoryFilter: '',
};

// Generic get/set helpers
const getItem = (key, defaultValue = null) => {
    try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
    } catch (e) {
        console.error(`Error reading ${key} from localStorage:`, e);
        return defaultValue;
    }
};

const setItem = (key, value) => {
    try {
        localStorage.setItem(key, JSON.stringify(value));
        return true;
    } catch (e) {
        console.error(`Error writing ${key} to localStorage:`, e);
        return false;
    }
};

// Config operations
export const getConfig = () => getItem(STORAGE_KEYS.CONFIG, DEFAULT_CONFIG);
export const saveConfig = (config) => setItem(STORAGE_KEYS.CONFIG, { ...DEFAULT_CONFIG, ...config });

// History operations
export const getHistory = () => getItem(STORAGE_KEYS.HISTORY, []);
export const saveHistory = (history) => setItem(STORAGE_KEYS.HISTORY, history);

// Queue operations
export const getQueue = () => getItem(STORAGE_KEYS.QUEUE, []);
export const saveQueue = (queue) => setItem(STORAGE_KEYS.QUEUE, queue);

// Stats operations
export const getStats = () => getItem(STORAGE_KEYS.STATS, { task_count: {}, total_executions: 0 });
export const saveStats = (stats) => setItem(STORAGE_KEYS.STATS, stats);

// Backup settings
export const getBackupSettings = () => getItem(STORAGE_KEYS.BACKUP_SETTINGS, DEFAULT_BACKUP_SETTINGS);
export const saveBackupSettings = (settings) => setItem(STORAGE_KEYS.BACKUP_SETTINGS, settings);

// Trash bin operations
export const getTrash = () => {
    const trash = getItem(STORAGE_KEYS.TRASH, []);
    // Auto cleanup expired items (older than 30 days)
    const now = Date.now();
    const validItems = trash.filter(item => {
        const deletedAt = new Date(item.deletedAt).getTime();
        const daysElapsed = (now - deletedAt) / (1000 * 60 * 60 * 24);
        return daysElapsed < TRASH_RETENTION_DAYS;
    });
    if (validItems.length !== trash.length) {
        setItem(STORAGE_KEYS.TRASH, validItems);
    }
    return validItems;
};

export const addToTrash = (item, itemType = 'task') => {
    const trash = getTrash();
    const trashItem = {
        ...item,
        itemType,
        deletedAt: new Date().toISOString(),
        trashId: `trash_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
    trash.unshift(trashItem);
    return setItem(STORAGE_KEYS.TRASH, trash);
};

export const restoreFromTrash = (trashId) => {
    const trash = getTrash();
    const index = trash.findIndex(item => item.trashId === trashId);
    if (index === -1) return null;

    const [restoredItem] = trash.splice(index, 1);
    setItem(STORAGE_KEYS.TRASH, trash);

    // Remove trash metadata
    const { deletedAt, trashId: _, itemType, ...originalItem } = restoredItem;
    return { item: originalItem, itemType };
};

export const permanentlyDeleteFromTrash = (trashId) => {
    const trash = getTrash();
    const newTrash = trash.filter(item => item.trashId !== trashId);
    return setItem(STORAGE_KEYS.TRASH, newTrash);
};

export const emptyTrash = () => {
    return setItem(STORAGE_KEYS.TRASH, []);
};

// Shortcuts operations
export const getShortcuts = () => getItem(STORAGE_KEYS.SHORTCUTS, []);
export const saveShortcuts = (shortcuts) => setItem(STORAGE_KEYS.SHORTCUTS, shortcuts);

// User preferences operations
export const getPreferences = () => getItem(STORAGE_KEYS.PREFERENCES, DEFAULT_PREFERENCES);
export const savePreferences = (prefs) => setItem(STORAGE_KEYS.PREFERENCES, { ...DEFAULT_PREFERENCES, ...prefs });

// Export all data
export const exportAllData = () => {
    const data = {
        version: '1.1',
        exportedAt: new Date().toISOString(),
        config: getConfig(),
        history: getHistory(),
        queue: getQueue(),
        stats: getStats(),
        backupSettings: getBackupSettings(),
        trash: getTrash(),
        shortcuts: getShortcuts(),
        preferences: getPreferences(),
    };
    return data;
};

// Import all data
export const importAllData = (data) => {
    try {
        if (data.config) saveConfig(data.config);
        if (data.history) saveHistory(data.history);
        if (data.queue) saveQueue(data.queue);
        if (data.stats) saveStats(data.stats);
        if (data.backupSettings) saveBackupSettings(data.backupSettings);
        if (data.trash) setItem(STORAGE_KEYS.TRASH, data.trash);
        if (data.shortcuts) saveShortcuts(data.shortcuts);
        if (data.preferences) savePreferences(data.preferences);
        return { success: true };
    } catch (e) {
        return { success: false, error: e.message };
    }
};

// Download data as JSON file
export const downloadBackup = () => {
    const data = exportAllData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `aiphone_backup_${new Date().toISOString().slice(0, 19).replace(/[:-]/g, '')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    // Update last backup time
    saveBackupSettings({ ...getBackupSettings(), lastBackupTime: new Date().toISOString() });
};

// Default export
export default {
    getConfig,
    saveConfig,
    getHistory,
    saveHistory,
    getQueue,
    saveQueue,
    getStats,
    saveStats,
    getBackupSettings,
    saveBackupSettings,
    getTrash,
    addToTrash,
    restoreFromTrash,
    permanentlyDeleteFromTrash,
    emptyTrash,
    getShortcuts,
    saveShortcuts,
    getPreferences,
    savePreferences,
    exportAllData,
    importAllData,
    downloadBackup,
    DEFAULT_CONFIG,
    DEFAULT_PREFERENCES,
    TRASH_RETENTION_DAYS,
};
