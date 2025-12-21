
const API_BASE = '/api';

export const api = {
    // Status & Polling
    getStatus: async () => {
        const res = await fetch(`${API_BASE}/status`);
        return res.json();
    },

    // Task Execution
    executeTask: async (task) => {
        const res = await fetch(`${API_BASE}/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task }),
        });
        return res.json();
    },

    stopTask: async () => {
        const res = await fetch(`${API_BASE}/stop`, { method: 'POST' });
        return res.json();
    },

    // Queue Management
    getQueue: async () => {
        const res = await fetch(`${API_BASE}/queue/list`);
        return res.json();
    },

    addToQueue: async (task) => {
        const res = await fetch(`${API_BASE}/queue/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task }),
        });
        return res.json();
    },

    removeFromQueue: async (taskId) => {
        const res = await fetch(`${API_BASE}/queue/remove`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId }),
        });
        return res.json();
    },

    // History & Stats
    getHistory: async (search = '') => {
        // Handling search param if needed
        const url = search ? `${API_BASE}/history?search=${encodeURIComponent(search)}` : `${API_BASE}/history`;
        const res = await fetch(url);
        return res.json();
    },

    deleteTask: async (id) => {
        const res = await fetch(`${API_BASE}/history/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id }),
        });
        return res.json();
    },

    moveToTrash: async (id) => {
        const res = await fetch(`${API_BASE}/trash/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id }),
        });
        return res.json();
    },

    deleteTaskStep: async (taskId, stepIndex) => {
        const res = await fetch(`${API_BASE}/history/step/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId, step_index: stepIndex }),
        });
        return res.json();
    },

    getPopular: async () => {
        const res = await fetch(`${API_BASE}/popular`);
        return res.json();
    },

    deletePopular: async (taskName) => {
        const res = await fetch(`${API_BASE}/popular/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task: taskName })
        });
        return res.json();
    },

    clearPopular: async () => {
        const res = await fetch(`${API_BASE}/popular/clear`, { method: 'POST' });
        return res.json();
    },

    installKeyboard: async () => {
        const res = await fetch(`${API_BASE}/tools/install-keyboard`, { method: 'POST' });
        return res.json();
    },

    resetStatus: async (skipSave = false) => {
        const res = await fetch(`${API_BASE}/status/reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ skip_save: skipSave })
        });
        return res.json();
    },

    // Config Management
    updateConfig: async (config) => {
        const res = await fetch(`${API_BASE}/config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
        return res.json();
    },

    getConfig: async () => {
        const res = await fetch(`${API_BASE}/config`);
        return res.json();
    },

    // Chat API for Q&A mode (multi-turn conversation)
    chat: async (message, history = []) => {
        const res = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message, history })
        });
        return res.json();
    },

    // Shortcuts API
    getShortcuts: async (params = {}) => {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_BASE}/shortcuts${query ? '?' + query : ''}`);
        return res.json();
    },

    addShortcut: async (shortcut) => {
        const res = await fetch(`${API_BASE}/shortcuts/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(shortcut)
        });
        return res.json();
    },

    updateShortcut: async (shortcut) => {
        const res = await fetch(`${API_BASE}/shortcuts/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(shortcut)
        });
        return res.json();
    },

    deleteShortcut: async (id) => {
        const res = await fetch(`${API_BASE}/shortcuts/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });
        return res.json();
    },

    reorderShortcuts: async (orderMap) => {
        const res = await fetch(`${API_BASE}/shortcuts/reorder`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ orderMap })
        });
        return res.json();
    },

    useShortcut: async (id) => {
        const res = await fetch(`${API_BASE}/shortcuts/use`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id })
        });
        return res.json();
    },

    syncShortcuts: async (shortcuts) => {
        const res = await fetch(`${API_BASE}/shortcuts/sync`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ shortcuts })
        });
        return res.json();
    }
};
