
import React, { useState, useEffect, useRef } from 'react';
import { api } from './services/api';
import storage from './services/storage';
import LogViewer from './components/log-viewer/LogViewer';
import SettingsModal from './components/SettingsModal';
import TrashModal from './components/TrashModal';
import { Toaster, toast } from 'react-hot-toast';
import {
  Play, StopCircle, Plus, Clock, List, Search,
  Trash2, ChevronDown, ChevronRight, MoreVertical,
  RefreshCw, XCircle, Settings, MessageSquare, Smartphone
} from 'lucide-react';
import clsx from 'clsx';

// --- Sidebar Components ---

const SidebarSection = ({ title, count, children, isOpen, onToggle, expandable = false, actions }) => (
  <div className={clsx(expandable ? "flex-1 flex flex-col min-h-0" : "mb-4")}>
    <div
      className="flex items-center justify-between px-4 py-2 cursor-pointer hover:bg-white/5 transition-colors group shrink-0"
    >
      <div className="flex items-center gap-2" onClick={onToggle}>
        {isOpen ? <ChevronDown size={14} className="text-text-muted" /> : <ChevronRight size={14} className="text-text-muted" />}
        <span className="text-xs font-semibold text-text-primary">{title}</span>
        {count !== undefined && (
          <span className="bg-background-tertiary text-text-secondary text-[10px] px-2 py-0.5 rounded-full border border-white/5">
            {count}
          </span>
        )}
      </div>
      {/* VS Code style action buttons */}
      {actions && (
        <div className="flex items-center gap-0.5 opacity-0 group-hover:opacity-100 transition-opacity">
          {actions}
        </div>
      )}
    </div>
    <div className={clsx(
      "transition-all duration-300",
      expandable ? "flex-1 overflow-y-auto custom-scrollbar" : "overflow-y-auto custom-scrollbar",
      isOpen ? (expandable ? "opacity-100" : "max-h-[200px] opacity-100") : "max-h-0 opacity-0"
    )}>
      <div className="px-3 pb-2">
        {children}
      </div>
    </div>
  </div>
);

// VS Code style action button
const ActionButton = ({ icon: Icon, title, onClick, danger = false }) => (
  <button
    onClick={(e) => { e.stopPropagation(); onClick?.(); }}
    className={clsx(
      "p-1 rounded hover:bg-white/10 transition-colors",
      danger ? "text-text-muted hover:text-status-error" : "text-text-muted hover:text-text-primary"
    )}
    title={title}
  >
    <Icon size={14} />
  </button>
);

// Unified Sidebar Item component for all sections
const SidebarItem = ({
  item,
  onClick,
  onDelete,
  showStatus = false,
  showTimestamp = false,
  statusKey = 'status',
  titleKey = 'task'
}) => {
  // Determine mode tags based on step types
  const hasChat = item.steps?.some(s => s.type === 'user_message' || s.type === 'assistant_message');
  const hasPhone = item.steps?.some(s => s.type === 'action' || s.type === 'response' || s.type === 'thinking');

  return (
    <div
      className="group relative p-2 mb-1 bg-background-tertiary rounded text-sm cursor-pointer hover:bg-accent-primary/10 hover:ring-1 hover:ring-accent-primary/50 text-left border border-transparent transition-all"
      onClick={() => onClick?.(item)}
    >
      <div className="font-medium text-text-primary truncate mb-0.5 pr-6">
        {item[titleKey]}
      </div>
      {(showStatus || showTimestamp) && (
        <div className="text-[10px] text-text-muted flex items-center gap-2">
          <span>{showTimestamp ? item.timestamp : item.added_time || ''}</span>
          {hasChat && <span className="text-cyan-400">Chat</span>}
          {hasPhone && <span className="text-purple-400">Phone</span>}
          <span className="ml-auto">
            {showStatus && (
              <span className={clsx(
                "capitalize",
                item[statusKey] === 'success' && 'text-status-success',
                item[statusKey] === 'error' && 'text-status-error',
                item[statusKey] === 'running' && 'text-accent-primary animate-pulse',
                item[statusKey] === 'idle' && 'text-text-muted'
              )}>{item[statusKey]}</span>
            )}
          </span>
        </div>
      )}
      {onDelete && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onDelete(item);
          }}
          className="absolute right-1 top-2 p-1 text-text-muted hover:text-status-error hover:bg-background-secondary rounded opacity-0 group-hover:opacity-100 transition-all"
          title="删除"
        >
          <Trash2 size={12} />
        </button>
      )}
    </div>
  );
};


// --- Confirm Modal Component ---
const ConfirmModal = ({ isOpen, title, message, onConfirm, onCancel }) => {
  // Handle keyboard events
  React.useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        onConfirm?.();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onCancel?.();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onConfirm, onCancel]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={onCancel}
      />
      {/* Modal */}
      <div className="relative bg-background-secondary border border-white/10 rounded-xl p-6 max-w-sm w-full mx-4 shadow-2xl">
        <h3 className="text-lg font-semibold text-text-primary mb-2">{title}</h3>
        <p className="text-sm text-text-secondary mb-6">{message}</p>
        <div className="flex gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-white/5 rounded-lg transition-colors"
          >
            取消 <span className="text-text-muted text-xs">(Esc)</span>
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 text-sm bg-status-error hover:bg-status-error/80 text-white rounded-lg transition-colors"
            autoFocus
          >
            确认删除 <span className="text-white/70 text-xs">(Enter)</span>
          </button>
        </div>
      </div>
    </div>
  );
};

// --- Layout Component ---

export default function Layout() {
  // State
  const [status, setStatus] = useState({ running: false, task: '', status: 'idle', steps: [] });
  const [queue, setQueue] = useState([]);
  const [history, setHistory] = useState([]);
  const [popular, setPopular] = useState([]);
  const [inputTask, setInputTask] = useState('');

  // View Mode: 'live' or 'archived'
  const [viewMode, setViewMode] = useState('live');
  const [selectedTask, setSelectedTask] = useState(null); // For archived view

  // UI State
  const [sections, setSections] = useState({ queue: true, popular: true, history: true });
  const [popularSearch, setPopularSearch] = useState('');
  const [showPopularSearch, setShowPopularSearch] = useState(false);
  const [historySearch, setHistorySearch] = useState('');
  const [showHistorySearch, setShowHistorySearch] = useState(false);
  const [confirmModal, setConfirmModal] = useState({ isOpen: false, title: '', message: '', onConfirm: null });
  const [showSettings, setShowSettings] = useState(false);
  const [showTrash, setShowTrash] = useState(false);

  // Execution Mode: 'chat' (Q&A) or 'phone' (Phone Control)
  const [executionMode, setExecutionMode] = useState('phone');
  const [chatHistory, setChatHistory] = useState([]); // For multi-turn chat

  // Refs for polling and backup
  const pollingRef = useRef(null);
  const prevRunningRef = useRef(false);
  const backupTimerRef = useRef(null); // Track previous running state to avoid duplicate toasts

  // Initial Load
  useEffect(() => {
    loadAllData();
    startPolling();
    return () => stopPolling();
  }, []);

  // Auto backup timer
  useEffect(() => {
    const setupBackupTimer = () => {
      if (backupTimerRef.current) {
        clearInterval(backupTimerRef.current);
      }

      const settings = storage.getBackupSettings();
      if (settings.enabled && settings.intervalMinutes > 0) {
        backupTimerRef.current = setInterval(() => {
          storage.downloadBackup();
          toast.success('自动备份已完成');
        }, settings.intervalMinutes * 60 * 1000);
      }
    };

    setupBackupTimer();
    return () => {
      if (backupTimerRef.current) {
        clearInterval(backupTimerRef.current);
      }
    };
  }, [showSettings]); // Re-setup when settings change

  const startPolling = () => {
    if (pollingRef.current) return;
    pollingRef.current = setInterval(checkStatus, 1000);
  };

  const stopPolling = () => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  };

  const checkStatus = async () => {
    try {
      const data = await api.getStatus();

      // Detect state transitions using refs (outside of setState to avoid duplicates)
      const wasRunning = prevRunningRef.current;
      const isRunning = data.running;

      // Task just finished
      if (wasRunning && !isRunning) {
        if (data.status === 'success') toast.success('Task Completed Successfully!');
        else if (data.status === 'error') toast.error('Task Action Failed');
        loadHistory();
        loadQueue(); // Refresh queue after task completion
      }

      // Task just started
      if (!wasRunning && isRunning) {
        toast.success('Task Started');
        loadHistory();
      }

      // Update ref for next cycle
      prevRunningRef.current = isRunning;

      // Update state
      setStatus(prev => {
        // Detect task name change
        if (prev.task !== data.task && data.task) {
          setTimeout(() => loadHistory(), 0);
        }

        // In chat mode, don't overwrite local chat messages with backend data
        if (executionMode === 'chat' && prev.steps.length > 0) {
          // Only update running status, keep local steps
          return {
            ...prev,
            running: data.running,
            status: data.status,
            can_stop: data.can_stop,
            task_id: data.task_id
          };
        }

        // Always update if steps changed or status changed
        const stepsChanged = prev.steps.length !== data.steps.length;
        const statusChanged = prev.status !== data.status || prev.running !== data.running;
        const taskChanged = prev.task !== data.task;

        if (stepsChanged || statusChanged || taskChanged) {
          return data;
        }
        return prev;
      });

      // Simple sync for queue length without full reload every second
      if (data.queue_length !== queue.length) {
        loadQueue();
      }

    } catch (e) {
      console.error("Polling error", e);
    }
  };

  const loadAllData = async () => {
    await Promise.all([loadQueue(), loadHistory(), loadPopular()]);
  };

  const loadQueue = async () => {
    try {
      const res = await api.getQueue();
      if (res.success) setQueue(res.queue);
    } catch (e) { console.error(e) }
  };

  const loadHistory = async (search = '') => {
    try {
      const res = await api.getHistory(search);
      if (res.success) setHistory(res.history);
    } catch (e) { console.error(e) }
  };

  const loadPopular = async () => {
    try {
      const res = await api.getPopular();
      if (res.success) setPopular(res.popular);
    } catch (e) { console.error(e) }
  };

  const returnToLive = async () => {
    setViewMode('live');
    setSelectedTask(null);
    setInputTask('');
    setChatHistory([]); // Clear chat history for fresh start

    // Clear local steps for fresh start
    setStatus(prev => ({ ...prev, steps: [], task: '' }));

    // Always reset to create new session
    try {
      await api.resetStatus();
      toast("New Task Session Started");
      await loadHistory(); // Refresh history list immediately
    } catch (e) { console.error(e); }

    checkStatus();
  };

  const handleDeleteTask = async (id) => {
    // Check if this is the current live session (not in history file)
    const isCurrentSession = status.task_id === id;

    setConfirmModal({
      isOpen: true,
      title: isCurrentSession ? '清除当前会话' : '删除任务',
      message: isCurrentSession
        ? '确定要清除当前会话吗？这将开始一个新的空白会话。'
        : '确定要删除这个任务吗？任务将移入垃圾箱，30天后自动清除。',
      onConfirm: async () => {
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
        try {
          if (isCurrentSession) {
            // For current session, just reset (skip saving empty task)
            await api.resetStatus(true);
            toast.success("会话已清除");
            loadHistory();
          } else {
            // For archived tasks, move to trash instead of permanent delete
            const res = await api.moveToTrash(id);
            if (res.success) {
              toast.success("任务已移入垃圾箱");
              loadHistory();
              if (selectedTask && selectedTask.id === id) {
                returnToLive();
              }
            } else {
              // If task not found in history, it might be the current session
              // Try reset instead
              if (res.message && res.message.includes('not found')) {
                await api.resetStatus(true);
                toast.success("会话已清除");
                loadHistory();
              } else {
                toast.error(res.message || "删除失败");
              }
            }
          }
        } catch (e) {
          toast.error("操作失败");
        }
      }
    });
  };

  const handleDeleteStep = async (stepIndex) => {
    const targetTaskId = viewMode === 'live' ? status.task_id : selectedTask.id;
    if (!targetTaskId) return;

    setConfirmModal({
      isOpen: true,
      title: '删除消息',
      message: '确定要删除这条消息吗？',
      onConfirm: async () => {
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
        try {
          const res = await api.deleteTaskStep(targetTaskId, stepIndex);
          if (res.success) {
            toast.success("消息已删除");
            if (viewMode === 'archived') {
              const historyRes = await api.getHistory();
              if (historyRes.success) {
                setHistory(historyRes.history);
                const updatedTask = historyRes.history.find(t => t.id === selectedTask.id);
                if (updatedTask) setSelectedTask(updatedTask);
              }
            } else {
              toast("注意: 删除只影响保存的历史记录，不影响运行中的内存。");
            }
          }
        } catch (e) {
          toast.error("删除失败");
        }
      }
    });
  };

  // Actions
  const handleExecute = async () => {
    if (!inputTask.trim()) return;

    if (executionMode === 'chat') {
      // Chat mode - multi-turn Q&A without phone control
      const userMessage = inputTask.trim();
      setInputTask('');

      // Add user message to chat history UI
      const newUserStep = {
        type: 'user_message',
        content: userMessage,
        timestamp: new Date().toLocaleTimeString()
      };

      // Update status to show user message
      setStatus(prev => ({
        ...prev,
        steps: [...prev.steps, newUserStep],
        task: userMessage
      }));

      // Add to chat history for context
      const updatedHistory = [...chatHistory, { role: 'user', content: userMessage }];
      setChatHistory(updatedHistory);

      try {
        // Call chat API with history for multi-turn
        const res = await api.chat(userMessage, updatedHistory);
        if (res.success && res.response) {
          const assistantMessage = {
            type: 'assistant_message',
            content: res.response,
            timestamp: new Date().toLocaleTimeString()
          };
          setStatus(prev => ({
            ...prev,
            steps: [...prev.steps, assistantMessage]
          }));
          setChatHistory([...updatedHistory, { role: 'assistant', content: res.response }]);
        } else {
          toast.error(res.message || '聊天请求失败');
        }
      } catch (e) {
        toast.error('网络错误：无法发送聊天消息');
      }
    } else {
      // Phone mode - add to task queue for phone control
      try {
        const res = await api.addToQueue(inputTask);
        if (res.success) {
          setInputTask('');
          loadQueue();
          toast.success("任务已添加到队列");
          checkStatus();
        } else {
          toast.error(res.message || "Failed to add task");
        }
      } catch (e) {
        toast.error("Network Error: Could not add task");
      }
    }
  };

  const handleStop = async () => {
    try {
      const res = await api.stopTask();
      if (res.success) toast.success("Stop signal sent");
      else toast.error(res.message);
    } catch (e) {
      toast.error("Failed to stop task");
    }
  };

  const handleAddToQueue = async () => {
    if (!inputTask.trim()) return;
    try {
      const res = await api.addToQueue(inputTask);
      if (res.success) {
        toast.success("Added to queue");
        setInputTask('');
        loadQueue();
      } else {
        toast.error(res.message);
      }
    } catch (e) {
      toast.error("Failed to add to queue");
    }
  };

  const handleRemoveFromQueue = async (id) => {
    try {
      const res = await api.removeFromQueue(id);
      if (res.success) {
        toast.success("Removed from queue");
        loadQueue();
      }
    } catch (e) {
      toast.error("Failed to remove item");
    }
  };

  const handleDeletePopular = async (taskName) => {
    setConfirmModal({
      isOpen: true,
      title: '删除常用任务',
      message: `确定要删除常用任务「${taskName}」吗？`,
      onConfirm: async () => {
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
        try {
          const res = await api.deletePopular(taskName);
          if (res.success) {
            toast.success("已删除");
            loadPopular();
          } else {
            toast.error(res.message || "删除失败");
          }
        } catch (e) {
          toast.error("删除失败");
        }
      }
    });
  };

  const handleClearPopular = async () => {
    setConfirmModal({
      isOpen: true,
      title: '清空常用任务',
      message: '确定要清空所有常用任务吗？此操作无法撤销。',
      onConfirm: async () => {
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
        try {
          const res = await api.clearPopular();
          if (res.success) {
            toast.success('已清空');
            loadPopular();
          } else {
            toast.error(res.message || '清空失败');
          }
        } catch (e) {
          toast.error('清空失败');
        }
      }
    });
  };

  const handleClearQueue = async () => {
    setConfirmModal({
      isOpen: true,
      title: '清空任务队列',
      message: '确定要清空任务队列吗？',
      onConfirm: async () => {
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
        try {
          const res = await fetch('/api/queue/clear', { method: 'POST' });
          const data = await res.json();
          if (data.success) {
            toast.success('队列已清空');
            loadQueue();
          }
        } catch (e) {
          toast.error('清空失败');
        }
      }
    });
  };

  const handleClearHistory = async () => {
    setConfirmModal({
      isOpen: true,
      title: '清空任务历史',
      message: '确定要清空所有任务历史吗？此操作无法撤销。',
      onConfirm: async () => {
        setConfirmModal(prev => ({ ...prev, isOpen: false }));
        try {
          const res = await fetch('/api/history/clear', { method: 'POST' });
          const data = await res.json();
          if (data.success) {
            toast.success('历史记录已清空');
            loadHistory();
          }
        } catch (e) {
          toast.error('清空失败');
        }
      }
    });
  };

  const handleHistoryClick = (item) => {
    // If the clicked item is the currently running task, switch to live view
    if (item.status === 'running') {
      setViewMode('live');
      setSelectedTask(null);
      return;
    }

    // Switch to archived view
    setViewMode('archived');
    setSelectedTask(item);

    // We don't stop polling, but checkStatus loop will only update global 'status' not the view if in archived mode
    // Actually checkStatus logic I wrote earlier: 
    // "Always check for global running state... Return new data only if we are in live mode"
    // So if viewMode is archived, 'status' state might stale? 
    // No, I set it to update toast. 
    // But LogViewer uses 'status.steps' in Live mode.
    // In Archived mode, we will pass 'selectedTask.steps'.
  };

  return (
    <div className="flex h-screen bg-background-primary text-text-primary overflow-hidden font-sans">
      <Toaster position="top-center" toastOptions={{
        style: {
          background: '#333',
          color: '#fff',
          fontSize: '13px'
        }
      }} />

      {/* Confirm Modal */}
      <ConfirmModal
        isOpen={confirmModal.isOpen}
        title={confirmModal.title}
        message={confirmModal.message}
        onConfirm={confirmModal.onConfirm}
        onCancel={() => setConfirmModal(prev => ({ ...prev, isOpen: false }))}
      />

      {/* Settings Modal */}
      <SettingsModal
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
        onConfigChange={(config) => {
          // Send config to backend if needed
          api.updateConfig?.(config);
        }}
      />

      {/* Trash Modal */}
      <TrashModal
        isOpen={showTrash}
        onClose={() => setShowTrash(false)}
        onRestored={() => {
          loadHistory();
          toast.success('任务已恢复');
        }}
      />

      {/* Sidebar */}
      <div className="w-80 bg-background-secondary border-r border-white/5 flex flex-col shrink-0">
        <div className="p-5 border-b border-white/5">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-8 h-8 bg-accent-primary rounded-lg flex items-center justify-center text-white shadow-lg shadow-accent-primary/20">
              <span className="font-bold text-lg">AI</span>
            </div>
            <h1 className="font-bold text-lg tracking-tight">AI Phone</h1>
          </div>
          <p className="text-xs text-text-muted ml-11">Smart Agent Controller</p>
        </div>

        <div className="flex-1 flex flex-col py-4 min-h-0">
          <SidebarSection
            title="Task Queue"
            count={queue.length}
            isOpen={sections.queue}
            onToggle={() => setSections(s => ({ ...s, queue: !s.queue }))}
            actions={
              <>
                <ActionButton
                  icon={RefreshCw}
                  title="刷新"
                  onClick={loadQueue}
                />
                <ActionButton
                  icon={XCircle}
                  title="清空队列"
                  onClick={handleClearQueue}
                  danger
                />
              </>
            }
          >
            {queue.length === 0 && <div className="text-xs text-text-muted p-2 text-center">Empty Queue</div>}
            {queue.map(item => (
              <SidebarItem
                key={item.id}
                item={item}
                onDelete={(i) => handleRemoveFromQueue(i.id)}
              />
            ))}
          </SidebarSection>

          <SidebarSection
            title="Popular Tasks"
            count={popular.length}
            isOpen={sections.popular}
            onToggle={() => setSections(s => ({ ...s, popular: !s.popular }))}
            actions={
              <>
                <ActionButton
                  icon={Search}
                  title="搜索"
                  onClick={() => setShowPopularSearch(!showPopularSearch)}
                />
                <ActionButton
                  icon={RefreshCw}
                  title="刷新"
                  onClick={loadPopular}
                />
                <ActionButton
                  icon={XCircle}
                  title="清空全部"
                  onClick={handleClearPopular}
                  danger
                />
              </>
            }
          >
            {/* Search input */}
            {showPopularSearch && (
              <div className="relative mb-2">
                <Search size={12} className="absolute left-2 top-2 text-text-muted" />
                <input
                  type="text"
                  placeholder="搜索常用任务..."
                  value={popularSearch}
                  onChange={(e) => setPopularSearch(e.target.value)}
                  className="w-full bg-background-primary border border-white/10 rounded pl-7 pr-2 py-1 text-xs focus:ring-1 focus:ring-accent-primary outline-none"
                  autoFocus
                />
              </div>
            )}
            {popular
              .filter(item => item.task.toLowerCase().includes(popularSearch.toLowerCase()))
              .slice(0, 8)
              .map(item => (
                <SidebarItem
                  key={item.task}
                  item={item}
                  onClick={(i) => setInputTask(i.task)}
                  onDelete={(i) => handleDeletePopular(i.task)}
                />
              ))}
            {popular.filter(item => item.task.toLowerCase().includes(popularSearch.toLowerCase())).length === 0 && (
              <div className="text-xs text-text-muted p-2 text-center">无匹配结果</div>
            )}
          </SidebarSection>

          <SidebarSection
            title="Tasks"
            count={history.length}
            isOpen={sections.history}
            onToggle={() => setSections(s => ({ ...s, history: !s.history }))}
            expandable={true}
            actions={
              <>
                <ActionButton
                  icon={Plus}
                  title="新建任务"
                  onClick={returnToLive}
                />
                <ActionButton
                  icon={Search}
                  title="搜索"
                  onClick={() => setShowHistorySearch(!showHistorySearch)}
                />
                <ActionButton
                  icon={RefreshCw}
                  title="刷新"
                  onClick={() => loadHistory()}
                />
                <ActionButton
                  icon={XCircle}
                  title="清空历史"
                  onClick={handleClearHistory}
                  danger
                />
                <ActionButton
                  icon={Trash2}
                  title="垃圾箱"
                  onClick={() => setShowTrash(true)}
                />
              </>
            }
          >
            <button
              onClick={returnToLive}
              className="w-full mb-3 flex items-center justify-center gap-2 bg-accent-primary hover:bg-accent-secondary text-white py-2 rounded-lg text-xs font-semibold shadow-lg shadow-accent-primary/20 transition-all"
            >
              <Plus size={14} /> New Task
            </button>

            {showHistorySearch && (
              <div className="relative mb-2">
                <Search size={12} className="absolute left-2 top-2 text-text-muted" />
                <input
                  type="text"
                  placeholder="搜索任务..."
                  value={historySearch}
                  onChange={(e) => {
                    setHistorySearch(e.target.value);
                    loadHistory(e.target.value);
                  }}
                  className="w-full bg-background-primary border border-white/10 rounded pl-7 pr-2 py-1 text-xs focus:ring-1 focus:ring-accent-primary outline-none"
                  autoFocus
                />
              </div>
            )}
            {history.map(item => (
              <SidebarItem
                key={item.id}
                item={item}
                onClick={handleHistoryClick}
                onDelete={(i) => handleDeleteTask(i.id)}
                showStatus
                showTimestamp
              />
            ))}
          </SidebarSection>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="h-16 border-b border-white/5 bg-background-secondary/50 backdrop-blur flex items-center justify-between px-6 shrink-0 z-10">
          <div className="flex flex-col">
            <span className="text-xs text-text-muted font-medium uppercase tracking-wider">
              {viewMode === 'live' ? 'Live Execution' : 'Archived Task'}
            </span>
            <div className="flex items-center gap-2">
              <span className="font-semibold text-text-primary truncate max-w-md" title={viewMode === 'live' ? status.task : selectedTask?.task}>
                {viewMode === 'live' ? (status.task || "Waiting for task...") : selectedTask?.task}
              </span>
              {/* Status Badge */}
              <span className={clsx(
                "text-[10px] px-2 py-0.5 rounded-full border uppercase font-bold tracking-wide",
                (viewMode === 'live' ? status.status : selectedTask?.status) === 'running' && "bg-accent-primary/10 text-accent-primary border-accent-primary/20 animate-pulse",
                (viewMode === 'live' ? status.status : selectedTask?.status) === 'success' && "bg-status-success/10 text-status-success border-status-success/20",
                (viewMode === 'live' ? status.status : selectedTask?.status) === 'error' && "bg-status-error/10 text-status-error border-status-error/20",
                (viewMode === 'live' ? status.status : selectedTask?.status) === 'idle' && "bg-text-muted/10 text-text-muted border-text-muted/20",
              )}>
                {viewMode === 'live' ? status.status : selectedTask?.status}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <button
              title="设置"
              onClick={() => setShowSettings(true)}
              className="p-2 text-text-secondary hover:text-text-primary hover:bg-white/5 rounded transition-colors"
            >
              <Settings size={18} />
            </button>
            {status.running && viewMode === 'live' && (
              <button
                onClick={handleStop}
                disabled={!status.can_stop}
                className="flex items-center gap-2 bg-background-primary border border-status-error text-status-error px-4 py-1.5 rounded-md text-sm font-medium hover:bg-status-error hover:text-white transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <StopCircle size={16} /> Stop Task
              </button>
            )}
          </div>
        </header>

        {/* Log Viewer */}
        <div className="flex-1 overflow-hidden relative bg-black/20">
          <LogViewer
            logs={viewMode === 'live' ? status.steps : (selectedTask?.steps || [])}
            autoScroll={viewMode === 'live'}
            onDeleteStep={handleDeleteStep}
          />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-white/5 bg-background-secondary shrink-0">
          {/* Mode Toggle */}
          <div className="max-w-4xl mx-auto mb-3 flex items-center gap-2">
            <span className="text-xs text-text-muted mr-2">模式:</span>
            <button
              onClick={() => setExecutionMode('chat')}
              className={clsx(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                executionMode === 'chat'
                  ? "bg-accent-primary text-white shadow-lg shadow-accent-primary/20"
                  : "bg-background-tertiary text-text-secondary hover:bg-white/10"
              )}
            >
              <MessageSquare size={14} />
              问答对话
            </button>
            <button
              onClick={() => setExecutionMode('phone')}
              className={clsx(
                "flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all",
                executionMode === 'phone'
                  ? "bg-accent-primary text-white shadow-lg shadow-accent-primary/20"
                  : "bg-background-tertiary text-text-secondary hover:bg-white/10"
              )}
            >
              <Smartphone size={14} />
              操控手机
            </button>
            {executionMode === 'chat' && chatHistory.length > 0 && (
              <button
                onClick={() => setChatHistory([])}
                className="ml-auto text-xs text-text-muted hover:text-status-error transition-colors"
              >
                清空对话历史 ({chatHistory.length} 条)
              </button>
            )}
          </div>

          <div className="relative flex gap-2 max-w-4xl mx-auto">
            <textarea
              value={inputTask}
              onChange={(e) => setInputTask(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  handleExecute();
                }
              }}
              placeholder="Describe your task here... (Ctrl + Enter to execute)"
              className="flex-1 bg-background-primary border border-white/10 rounded-lg p-3 text-sm focus:outline-none focus:ring-2 focus:ring-accent-primary/50 resize-none h-14"
            />
            <button
              onClick={handleExecute}
              disabled={status.running}
              className="bg-accent-primary hover:bg-accent-secondary text-white px-6 rounded-lg font-medium shadow-lg shadow-accent-primary/20 disabled:opacity-50 disabled:cursor-not-allowed flex flex-col items-center justify-center gap-0.5 min-w-[80px] transition-all"
            >
              <Play size={18} fill="currentColor" className={clsx(status.running && "hidden")} />
              <span className="text-xs">{status.running ? 'Running' : 'Run'}</span>
            </button>

            <button
              onClick={handleAddToQueue}
              className="bg-background-tertiary hover:bg-white/10 text-text-secondary w-10 rounded-lg flex items-center justify-center border border-white/5 transition-all"
              title="Add to Queue"
            >
              <Plus size={20} />
            </button>
          </div>
          <div className="max-w-4xl mx-auto mt-2 flex justify-between text-[10px] text-text-muted">
            <span>Tip: Use specific instructions for better results.</span>
            <button onClick={() => setInputTask('')} className="hover:text-text-primary">Clear Input</button>
          </div>
        </div>
      </div>
    </div>
  );
}
