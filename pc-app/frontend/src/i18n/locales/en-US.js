// English (US) translations
const enUS = {
    // App - Sidebar
    sidebar: {
        appName: 'AI Phone',
        appDesc: 'Smart Agent Controller',
        taskQueue: 'Task Queue',
        popularTasks: 'Popular Tasks',
        tasks: 'Tasks',
        emptyQueue: 'Empty Queue',
        noResults: 'No matching results',
        newTask: 'New Task',
        searchPopular: 'Search popular tasks...',
        searchTasks: 'Search tasks...',
    },

    // App - Header
    header: {
        liveExecution: 'Live Execution',
        archivedTask: 'Archived Task',
        waitingForTask: 'Waiting for task...',
        settings: 'Settings',
        stopTask: 'Stop Task',
    },

    // App - Status
    status: {
        running: 'Running',
        success: 'Success',
        error: 'Error',
        idle: 'Idle',
    },

    // App - Input Area
    input: {
        mode: 'Mode:',
        chat: 'Q&A Chat',
        phone: 'Phone Control',
        clearChatHistory: 'Clear chat history',
        messages: 'messages',
        placeholder: 'Describe your task here... (Ctrl + Enter to execute)',
        run: 'Run',
        tip: 'Tip: Use specific instructions for better results.',
        clearInput: 'Clear Input',
    },

    // App - Actions
    actions: {
        refresh: 'Refresh',
        clearQueue: 'Clear Queue',
        search: 'Search',
        clearAll: 'Clear All',
        clearHistory: 'Clear History',
        trash: 'Trash',
        delete: 'Delete',
    },

    // App - Toasts & Dialogs
    toast: {
        configureApiKey: 'Please configure API Key first',
        taskCompleted: 'Task Completed Successfully!',
        taskFailed: 'Task Action Failed',
        taskStarted: 'Task Started',
        taskAddedToQueue: 'Task added to queue',
        addedToQueue: 'Added to queue',
        removedFromQueue: 'Removed from queue',
        stopSignalSent: 'Stop signal sent',
        deleted: 'Deleted',
        sessionCleared: 'Session cleared',
        movedToTrash: 'Task moved to trash',
        deleteFailed: 'Delete failed',
        operationFailed: 'Operation failed',
        messageDeleted: 'Message deleted',
        deleteNoteMemory: 'Note: Deletion only affects saved history, not running memory.',
        queueCleared: 'Queue cleared',
        historyCleared: 'History cleared',
        clearFailed: 'Clear failed',
        popularCleared: 'Cleared',
        newTaskSession: 'New Task Session Started',
        chatError: 'Chat request failed',
        networkErrorChat: 'Network Error: Could not send chat message',
        networkErrorTask: 'Network Error: Could not add task',
        failedToStop: 'Failed to stop task',
        failedToAdd: 'Failed to add to queue',
        failedToRemove: 'Failed to remove item',
        taskRestored: 'Task restored',
        autoBackupComplete: 'Auto backup completed',
    },

    // Confirm Dialogs
    confirm: {
        clearCurrentSession: 'Clear Current Session',
        deleteTask: 'Delete Task',
        clearSessionMessage: 'Are you sure you want to clear the current session? This will start a new blank session.',
        deleteTaskMessage: 'Are you sure you want to delete this task? It will be moved to trash and auto-deleted after 30 days.',
        deleteMessage: 'Delete Message',
        deleteMessageConfirm: 'Are you sure you want to delete this message?',
        deletePopularTask: 'Delete Popular Task',
        deletePopularConfirm: 'Are you sure you want to delete popular task "{task}"?',
        clearPopularTasks: 'Clear Popular Tasks',
        clearPopularConfirm: 'Are you sure you want to clear all popular tasks? This cannot be undone.',
        clearTaskQueue: 'Clear Task Queue',
        clearQueueConfirm: 'Are you sure you want to clear the task queue?',
        clearTaskHistory: 'Clear Task History',
        clearHistoryConfirm: 'Are you sure you want to clear all task history? This cannot be undone.',
        cancel: 'Cancel',
        confirmDelete: 'Confirm Delete',
    },

    // Settings Modal
    settings: {
        title: 'Settings',
        tabs: {
            api: 'API Config',
            data: 'Data Management',
            backup: 'Auto Backup',
            language: 'Language',
        },
        api: {
            baseUrl: 'Base URL',
            modelName: 'Model Name',
            apiKey: 'API Key',
            apiKeyHelp: 'API Key is used to access Zhipu AI model services.',
            apiKeyHelpExtra: 'If you don\'t have an API Key, register at Zhipu Open Platform to get one.',
            getApiKey: 'Get API Key',
            placeholder: 'Enter your API Key',
            save: 'Save Configuration',
        },
        data: {
            exportTitle: 'Export Data',
            exportDesc: 'Export all task history, configuration and statistics to a JSON file.',
            exportButton: 'Export Backup',
            importTitle: 'Import Data',
            importDesc: 'Restore data from a JSON backup file. This will overwrite all current data.',
            importButton: 'Select File to Import',
            importing: 'Importing...',
            statsTitle: 'Statistics',
            taskRecords: 'Task Records',
            queueTasks: 'Queue Tasks',
            importSuccess: 'Import successful! Page will refresh to load new data.',
            importFailed: 'Import failed: ',
            fileFormatError: 'File format error: ',
        },
        backup: {
            autoBackup: 'Auto Backup',
            autoBackupDesc: 'Automatically download backup files to default download directory',
            interval: 'Backup Interval',
            intervals: {
                30: '30 minutes',
                60: '1 hour',
                120: '2 hours',
                1440: '24 hours',
            },
            lastBackupTime: 'Last Backup Time',
            backupNow: 'Backup Now',
        },
        language: {
            title: 'Interface Language',
            desc: 'Select the display language for the application',
            chinese: '简体中文',
            english: 'English',
        },
    },

    // Trash Modal
    trash: {
        title: 'Trash',
        empty: 'Trash is empty',
        emptyDesc: 'Deleted tasks will appear here and auto-delete after 30 days',
        restore: 'Restore',
        deletePermanently: 'Delete Permanently',
        emptyTrash: 'Empty Trash',
        emptyTrashConfirm: 'Are you sure you want to permanently delete all trash contents? This cannot be undone.',
        deleteConfirm: 'Are you sure you want to permanently delete this task? This cannot be undone.',
        daysRemaining: 'days until auto-delete',
        permanentDelete: 'Permanent Delete',
    },

    // Log Viewer
    log: {
        executeAction: 'Execute Action',
        modelResponse: 'Model Response',
        user: 'User',
        me: 'Me',
        assistant: 'Assistant',
        thinking: 'Thinking...',
        taskStart: '🚀 Task Started:',
        ready: 'Ready to execute tasks',
        scrollToTop: 'Scroll to top',
        deleteMessage: 'Delete message',
    },

    // Common
    common: {
        chat: 'Chat',
        phone: 'Phone',
    },
};

export default enUS;
