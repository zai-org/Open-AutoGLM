// Chinese (Simplified) translations
const zhCN = {
    // App - Sidebar
    sidebar: {
        appName: 'AI Phone',
        appDesc: '智能代理控制器',
        taskQueue: '任务队列',
        popularTasks: '常用任务',
        tasks: '任务',
        emptyQueue: '队列为空',
        noResults: '无匹配结果',
        newTask: '新建任务',
        searchPopular: '搜索常用任务...',
        searchTasks: '搜索任务...',
    },

    // App - Header
    header: {
        liveExecution: '实时执行',
        archivedTask: '历史任务',
        waitingForTask: '等待任务...',
        settings: '设置',
        stopTask: '停止任务',
    },

    // App - Status
    status: {
        running: '运行中',
        success: '成功',
        error: '错误',
        idle: '空闲',
    },

    // App - Input Area
    input: {
        mode: '模式:',
        chat: '问答对话',
        phone: '操控手机',
        clearChatHistory: '清空对话历史',
        messages: '条',
        placeholder: '在此输入您的任务... (Ctrl + Enter 执行)',
        run: '执行',
        tip: '提示: 使用具体指令以获得更好效果。',
        clearInput: '清空输入',
    },

    // App - Actions
    actions: {
        refresh: '刷新',
        clearQueue: '清空队列',
        search: '搜索',
        clearAll: '清空全部',
        clearHistory: '清空历史',
        trash: '垃圾箱',
        delete: '删除',
    },

    // App - Toasts & Dialogs
    toast: {
        configureApiKey: '请先配置 API Key 才能使用',
        taskCompleted: '任务执行成功!',
        taskFailed: '任务执行失败',
        taskStarted: '任务已开始',
        taskAddedToQueue: '任务已添加到队列',
        addedToQueue: '已添加到队列',
        removedFromQueue: '已从队列移除',
        stopSignalSent: '停止信号已发送',
        deleted: '已删除',
        sessionCleared: '会话已清除',
        movedToTrash: '任务已移入垃圾箱',
        deleteFailed: '删除失败',
        operationFailed: '操作失败',
        messageDeleted: '消息已删除',
        deleteNoteMemory: '注意: 删除只影响保存的历史记录，不影响运行中的内存。',
        queueCleared: '队列已清空',
        historyCleared: '历史记录已清空',
        clearFailed: '清空失败',
        popularCleared: '已清空',
        newTaskSession: '新任务会话已开始',
        chatError: '聊天请求失败',
        networkErrorChat: '网络错误：无法发送聊天消息',
        networkErrorTask: '网络错误: 无法添加任务',
        failedToStop: '无法停止任务',
        failedToAdd: '无法添加到队列',
        failedToRemove: '无法移除',
        taskRestored: '任务已恢复',
        autoBackupComplete: '自动备份已完成',
    },

    // Confirm Dialogs
    confirm: {
        clearCurrentSession: '清除当前会话',
        deleteTask: '删除任务',
        clearSessionMessage: '确定要清除当前会话吗？这将开始一个新的空白会话。',
        deleteTaskMessage: '确定要删除这个任务吗？任务将移入垃圾箱，30天后自动清除。',
        deleteMessage: '删除消息',
        deleteMessageConfirm: '确定要删除这条消息吗？',
        deletePopularTask: '删除常用任务',
        deletePopularConfirm: '确定要删除常用任务「{task}」吗？',
        clearPopularTasks: '清空常用任务',
        clearPopularConfirm: '确定要清空所有常用任务吗？此操作无法撤销。',
        clearTaskQueue: '清空任务队列',
        clearQueueConfirm: '确定要清空任务队列吗？',
        clearTaskHistory: '清空任务历史',
        clearHistoryConfirm: '确定要清空所有任务历史吗？此操作无法撤销。',
        cancel: '取消',
        confirmDelete: '确认删除',
    },

    // Settings Modal
    settings: {
        title: '设置',
        tabs: {
            api: 'API 配置',
            data: '数据管理',
            backup: '自动备份',
            language: '语言',
        },
        api: {
            baseUrl: 'Base URL',
            modelName: '模型名称',
            apiKey: 'API Key',
            apiKeyHelp: 'API Key 用于调用智谱 AI 模型服务。',
            apiKeyHelpExtra: '如果没有 API Key，请前往智谱开放平台注册获取。',
            getApiKey: '获取 API Key',
            placeholder: '请输入您的 API Key',
            save: '保存配置',
        },
        data: {
            exportTitle: '导出数据',
            exportDesc: '将所有任务历史、配置和统计数据导出为 JSON 文件。',
            exportButton: '导出备份',
            importTitle: '导入数据',
            importDesc: '从 JSON 备份文件恢复数据。这将覆盖当前所有数据。',
            importButton: '选择文件导入',
            importing: '导入中...',
            statsTitle: '数据统计',
            taskRecords: '任务记录',
            queueTasks: '队列任务',
            importSuccess: '导入成功！页面将刷新以加载新数据。',
            importFailed: '导入失败：',
            fileFormatError: '文件格式错误：',
        },
        backup: {
            autoBackup: '自动备份',
            autoBackupDesc: '定时自动下载备份文件到默认下载目录',
            interval: '备份间隔',
            intervals: {
                30: '30 分钟',
                60: '1 小时',
                120: '2 小时',
                1440: '24 小时',
            },
            lastBackupTime: '上次备份时间',
            backupNow: '立即备份',
        },
        language: {
            title: '界面语言',
            desc: '选择应用界面的显示语言',
            chinese: '简体中文',
            english: 'English',
        },
    },

    // Trash Modal
    trash: {
        title: '垃圾箱',
        empty: '垃圾箱为空',
        emptyDesc: '删除的任务将在此显示，30天后自动清除',
        restore: '恢复',
        deletePermanently: '永久删除',
        emptyTrash: '清空垃圾箱',
        emptyTrashConfirm: '确定要永久删除所有垃圾箱内容吗？此操作无法撤销。',
        deleteConfirm: '确定要永久删除这个任务吗？此操作无法撤销。',
        daysRemaining: '天后自动删除',
        permanentDelete: '永久删除',
    },

    // Log Viewer
    log: {
        executeAction: '执行动作',
        modelResponse: '模型回复',
        user: '用户',
        me: '我',
        assistant: '助手',
        thinking: '思考中...',
        taskStart: '🚀 任务开始:',
        ready: '准备执行任务',
        scrollToTop: '回到顶部',
        deleteMessage: '删除消息',
    },

    // Common
    common: {
        chat: 'Chat',
        phone: 'Phone',
    },
};

export default zhCN;
