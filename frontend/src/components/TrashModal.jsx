import React, { useState, useEffect } from 'react';
import { X, Trash2, RotateCcw, Clock, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';

export default function TrashModal({ isOpen, onClose, onRestored }) {
    const [trash, setTrash] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            loadTrash();
        }
    }, [isOpen]);

    const loadTrash = async () => {
        setLoading(true);
        try {
            const res = await fetch('/api/trash');
            const data = await res.json();
            if (data.success) {
                setTrash(data.trash || []);
            }
        } catch (e) {
            console.error('Failed to load trash:', e);
        }
        setLoading(false);
    };

    const handleRestore = async (trashId) => {
        try {
            const res = await fetch('/api/trash/restore', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ trashId })
            });
            const data = await res.json();
            if (data.success) {
                setTrash(prev => prev.filter(item => item.trashId !== trashId));
                onRestored?.();
            }
        } catch (e) {
            console.error('Failed to restore:', e);
        }
    };

    const handlePermanentDelete = async (trashId) => {
        try {
            const res = await fetch('/api/trash/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ trashId })
            });
            const data = await res.json();
            if (data.success) {
                setTrash(prev => prev.filter(item => item.trashId !== trashId));
            }
        } catch (e) {
            console.error('Failed to delete:', e);
        }
    };

    const handleEmptyTrash = async () => {
        if (!confirm('确定要清空垃圾箱吗？此操作不可撤销。')) return;
        try {
            const res = await fetch('/api/trash/clear', { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                setTrash([]);
            }
        } catch (e) {
            console.error('Failed to empty trash:', e);
        }
    };

    const getDaysRemaining = (deletedAt) => {
        const deleted = new Date(deletedAt);
        const now = new Date();
        const daysElapsed = Math.floor((now - deleted) / (1000 * 60 * 60 * 24));
        return Math.max(0, 30 - daysElapsed);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

            {/* Modal */}
            <div className="relative bg-background-secondary border border-white/10 rounded-xl w-full max-w-2xl mx-4 shadow-2xl overflow-hidden max-h-[80vh] flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 shrink-0">
                    <div className="flex items-center gap-3">
                        <Trash2 size={20} className="text-status-error" />
                        <h2 className="text-lg font-semibold text-text-primary">垃圾箱</h2>
                        <span className="text-xs text-text-muted bg-background-tertiary px-2 py-0.5 rounded-full">
                            {trash.length} 项
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {trash.length > 0 && (
                            <button
                                onClick={handleEmptyTrash}
                                className="text-xs text-status-error hover:bg-status-error/10 px-3 py-1.5 rounded-lg transition-colors"
                            >
                                清空垃圾箱
                            </button>
                        )}
                        <button onClick={onClose} className="p-1 text-text-muted hover:text-text-primary transition-colors">
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto custom-scrollbar p-4">
                    {loading ? (
                        <div className="flex items-center justify-center py-12 text-text-muted">
                            加载中...
                        </div>
                    ) : trash.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 text-text-muted">
                            <Trash2 size={48} strokeWidth={1} className="mb-4 opacity-30" />
                            <p className="text-sm">垃圾箱是空的</p>
                            <p className="text-xs mt-1 opacity-50">删除的任务会在这里保留 30 天</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {trash.map((item) => (
                                <div
                                    key={item.trashId}
                                    className="bg-background-tertiary rounded-lg p-4 border border-white/5 hover:border-white/10 transition-colors"
                                >
                                    <div className="flex items-start justify-between gap-4">
                                        <div className="flex-1 min-w-0">
                                            <p className="text-sm text-text-primary truncate font-medium">
                                                {item.task || '未命名任务'}
                                            </p>
                                            <div className="flex items-center gap-3 mt-2 text-xs text-text-muted">
                                                <span className="flex items-center gap-1">
                                                    <Clock size={12} />
                                                    删除于 {new Date(item.deletedAt).toLocaleString('zh-CN')}
                                                </span>
                                                <span className="flex items-center gap-1 text-status-warning">
                                                    <AlertTriangle size={12} />
                                                    {getDaysRemaining(item.deletedAt)} 天后自动删除
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-2 shrink-0">
                                            <button
                                                onClick={() => handleRestore(item.trashId)}
                                                className="flex items-center gap-1 px-3 py-1.5 text-xs bg-accent-primary/10 text-accent-primary hover:bg-accent-primary/20 rounded-lg transition-colors"
                                                title="恢复"
                                            >
                                                <RotateCcw size={14} />
                                                恢复
                                            </button>
                                            <button
                                                onClick={() => handlePermanentDelete(item.trashId)}
                                                className="flex items-center gap-1 px-3 py-1.5 text-xs bg-status-error/10 text-status-error hover:bg-status-error/20 rounded-lg transition-colors"
                                                title="永久删除"
                                            >
                                                <Trash2 size={14} />
                                                删除
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Footer hint */}
                <div className="px-6 py-3 border-t border-white/5 text-xs text-text-muted text-center shrink-0">
                    删除的任务会保留 30 天，之后将自动永久删除
                </div>
            </div>
        </div>
    );
}
