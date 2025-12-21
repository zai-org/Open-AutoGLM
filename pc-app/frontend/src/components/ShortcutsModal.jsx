// ShortcutsModal.jsx - 快捷指令管理弹窗
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import storage from '../services/storage';
import {
    X, Plus, Edit2, Trash2, Search, ChevronLeft, ChevronRight,
    GripVertical, Zap, Play, Filter
} from 'lucide-react';
import clsx from 'clsx';
import { useLanguage } from '../i18n/i18n.jsx';

export default function ShortcutsModal({ isOpen, onClose, onUseShortcut }) {
    const { t } = useLanguage();

    // Data state
    const [shortcuts, setShortcuts] = useState([]);
    const [categories, setCategories] = useState([]);
    const [total, setTotal] = useState(0);
    const [totalPages, setTotalPages] = useState(1);

    // Filter/pagination state
    const [search, setSearch] = useState('');
    const [category, setCategory] = useState('');
    const [page, setPage] = useState(1);
    const [pageSize, setPageSize] = useState(() => {
        const prefs = storage.getPreferences();
        return prefs.shortcutsPageSize || 10;
    });

    // UI state
    const [loading, setLoading] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [editingShortcut, setEditingShortcut] = useState(null);
    const [draggedId, setDraggedId] = useState(null);

    // Form state
    const [formData, setFormData] = useState({ name: '', command: '', category: '其他' });

    // Load data on mount and when filters change
    useEffect(() => {
        if (isOpen) {
            loadShortcuts();
        }
    }, [isOpen, search, category, page, pageSize]);

    const loadShortcuts = async () => {
        setLoading(true);
        try {
            const res = await api.getShortcuts({ search, category, page, pageSize });
            if (res.success) {
                setShortcuts(res.shortcuts || []);
                setCategories(res.categories || []);
                setTotal(res.total || 0);
                setTotalPages(res.totalPages || 1);
            }
        } catch (e) {
            console.error('Failed to load shortcuts:', e);
        }
        setLoading(false);
    };

    // Save page size preference
    const handlePageSizeChange = (newSize) => {
        setPageSize(newSize);
        setPage(1);
        storage.savePreferences({ ...storage.getPreferences(), shortcutsPageSize: newSize });
    };

    // Form handlers
    const openAddForm = () => {
        setFormData({ name: '', command: '', category: '其他' });
        setEditingShortcut(null);
        setShowForm(true);
    };

    const openEditForm = (shortcut) => {
        setFormData({
            name: shortcut.name,
            command: shortcut.command,
            category: shortcut.category
        });
        setEditingShortcut(shortcut);
        setShowForm(true);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!formData.name.trim() || !formData.command.trim()) return;

        try {
            if (editingShortcut) {
                await api.updateShortcut({ id: editingShortcut.id, ...formData });
            } else {
                await api.addShortcut(formData);
            }
            setShowForm(false);
            loadShortcuts();
        } catch (e) {
            console.error('Failed to save shortcut:', e);
        }
    };

    const handleDelete = async (id) => {
        if (!confirm(t('shortcuts.confirmDelete'))) return;
        try {
            await api.deleteShortcut(id);
            loadShortcuts();
        } catch (e) {
            console.error('Failed to delete shortcut:', e);
        }
    };

    const handleUse = async (shortcut) => {
        await api.useShortcut(shortcut.id);
        onUseShortcut?.(shortcut.command);
        onClose();
    };

    // Drag and drop handlers
    const handleDragStart = (e, id) => {
        setDraggedId(id);
        e.dataTransfer.effectAllowed = 'move';
    };

    const handleDragOver = (e, targetId) => {
        e.preventDefault();
        if (draggedId === targetId) return;
    };

    const handleDrop = async (e, targetId) => {
        e.preventDefault();
        if (!draggedId || draggedId === targetId) return;

        const draggedIndex = shortcuts.findIndex(s => s.id === draggedId);
        const targetIndex = shortcuts.findIndex(s => s.id === targetId);

        if (draggedIndex === -1 || targetIndex === -1) return;

        // Reorder locally
        const newShortcuts = [...shortcuts];
        const [removed] = newShortcuts.splice(draggedIndex, 1);
        newShortcuts.splice(targetIndex, 0, removed);

        // Update order values
        const orderMap = {};
        newShortcuts.forEach((s, i) => {
            orderMap[s.id] = i + 1;
        });

        setShortcuts(newShortcuts);
        setDraggedId(null);

        // Sync to backend
        await api.reorderShortcuts(orderMap);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

            {/* Modal */}
            <div className="relative bg-background-secondary border border-white/10 rounded-xl w-full max-w-2xl max-h-[80vh] flex flex-col shadow-2xl mx-4">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/5">
                    <div className="flex items-center gap-2">
                        <Zap size={20} className="text-accent-primary" />
                        <h2 className="text-lg font-semibold text-text-primary">{t('shortcuts.title')}</h2>
                        <span className="text-xs text-text-muted bg-background-tertiary px-2 py-0.5 rounded-full">
                            {total} {t('shortcuts.items')}
                        </span>
                    </div>
                    <button onClick={onClose} className="p-1 text-text-muted hover:text-text-primary">
                        <X size={20} />
                    </button>
                </div>

                {/* Toolbar */}
                <div className="flex items-center gap-2 px-6 py-3 border-b border-white/5">
                    {/* Search */}
                    <div className="relative flex-1">
                        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                        <input
                            type="text"
                            placeholder={t('shortcuts.searchPlaceholder')}
                            value={search}
                            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                            className="w-full bg-background-primary border border-white/10 rounded-lg pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-primary"
                        />
                    </div>

                    {/* Category filter */}
                    <div className="relative">
                        <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" />
                        <select
                            value={category}
                            onChange={(e) => { setCategory(e.target.value); setPage(1); }}
                            className="bg-background-primary border border-white/10 rounded-lg pl-9 pr-8 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-primary appearance-none cursor-pointer"
                        >
                            <option value="">{t('shortcuts.allCategories')}</option>
                            {categories.map(cat => (
                                <option key={cat} value={cat}>{cat}</option>
                            ))}
                        </select>
                    </div>

                    {/* Add button */}
                    <button
                        onClick={openAddForm}
                        className="flex items-center gap-1.5 bg-accent-primary hover:bg-accent-secondary text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    >
                        <Plus size={16} />
                        {t('shortcuts.add')}
                    </button>
                </div>

                {/* List */}
                <div className="flex-1 overflow-y-auto px-6 py-3">
                    {loading ? (
                        <div className="text-center py-8 text-text-muted">{t('common.loading')}</div>
                    ) : shortcuts.length === 0 ? (
                        <div className="text-center py-12">
                            <Zap size={48} className="mx-auto text-text-muted/30 mb-3" />
                            <p className="text-text-muted">{t('shortcuts.empty')}</p>
                            <button
                                onClick={openAddForm}
                                className="mt-4 text-accent-primary hover:underline text-sm"
                            >
                                {t('shortcuts.addFirst')}
                            </button>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {shortcuts.map(shortcut => (
                                <div
                                    key={shortcut.id}
                                    draggable
                                    onDragStart={(e) => handleDragStart(e, shortcut.id)}
                                    onDragOver={(e) => handleDragOver(e, shortcut.id)}
                                    onDrop={(e) => handleDrop(e, shortcut.id)}
                                    className={clsx(
                                        "group flex items-center gap-3 p-3 bg-background-tertiary rounded-lg border border-transparent",
                                        "hover:border-accent-primary/30 transition-all cursor-grab active:cursor-grabbing",
                                        draggedId === shortcut.id && "opacity-50"
                                    )}
                                >
                                    {/* Drag handle */}
                                    <GripVertical size={16} className="text-text-muted/50 shrink-0" />

                                    {/* Content */}
                                    <div className="flex-1 min-w-0">
                                        <div className="flex items-center gap-2">
                                            <span className="font-medium text-text-primary truncate">{shortcut.name}</span>
                                            <span className="text-[10px] text-text-muted bg-background-secondary px-1.5 py-0.5 rounded">
                                                {shortcut.category}
                                            </span>
                                        </div>
                                        <div className="text-xs text-text-muted truncate mt-0.5">{shortcut.command}</div>
                                    </div>

                                    {/* Actions */}
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={() => handleUse(shortcut)}
                                            className="p-1.5 text-accent-primary hover:bg-accent-primary/10 rounded"
                                            title={t('shortcuts.use')}
                                        >
                                            <Play size={14} fill="currentColor" />
                                        </button>
                                        <button
                                            onClick={() => openEditForm(shortcut)}
                                            className="p-1.5 text-text-muted hover:text-text-primary hover:bg-white/5 rounded"
                                            title={t('shortcuts.edit')}
                                        >
                                            <Edit2 size={14} />
                                        </button>
                                        <button
                                            onClick={() => handleDelete(shortcut.id)}
                                            className="p-1.5 text-text-muted hover:text-status-error hover:bg-status-error/10 rounded"
                                            title={t('shortcuts.delete')}
                                        >
                                            <Trash2 size={14} />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-between px-6 py-3 border-t border-white/5">
                        <div className="flex items-center gap-2 text-xs text-text-muted">
                            <span>{t('shortcuts.pageSize')}:</span>
                            {[5, 10, 20].map(size => (
                                <button
                                    key={size}
                                    onClick={() => handlePageSizeChange(size)}
                                    className={clsx(
                                        "px-2 py-1 rounded",
                                        pageSize === size ? "bg-accent-primary text-white" : "hover:bg-white/5"
                                    )}
                                >
                                    {size}
                                </button>
                            ))}
                        </div>
                        <div className="flex items-center gap-2">
                            <button
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="p-1 text-text-muted hover:text-text-primary disabled:opacity-30"
                            >
                                <ChevronLeft size={18} />
                            </button>
                            <span className="text-sm text-text-secondary">
                                {page} / {totalPages}
                            </span>
                            <button
                                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                disabled={page === totalPages}
                                className="p-1 text-text-muted hover:text-text-primary disabled:opacity-30"
                            >
                                <ChevronRight size={18} />
                            </button>
                        </div>
                    </div>
                )}

                {/* Add/Edit Form Modal */}
                {showForm && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center rounded-xl">
                        <div className="bg-background-secondary border border-white/10 rounded-xl p-6 w-full max-w-md mx-4">
                            <h3 className="text-lg font-semibold text-text-primary mb-4">
                                {editingShortcut ? t('shortcuts.editTitle') : t('shortcuts.addTitle')}
                            </h3>
                            <form onSubmit={handleSubmit} className="space-y-4">
                                <div>
                                    <label className="block text-sm text-text-secondary mb-1">{t('shortcuts.name')}</label>
                                    <input
                                        type="text"
                                        value={formData.name}
                                        onChange={(e) => setFormData(d => ({ ...d, name: e.target.value }))}
                                        placeholder={t('shortcuts.namePlaceholder')}
                                        className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-primary"
                                        autoFocus
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-text-secondary mb-1">{t('shortcuts.command')}</label>
                                    <textarea
                                        value={formData.command}
                                        onChange={(e) => setFormData(d => ({ ...d, command: e.target.value }))}
                                        placeholder={t('shortcuts.commandPlaceholder')}
                                        rows={3}
                                        className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-primary resize-none"
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm text-text-secondary mb-1">{t('shortcuts.category')}</label>
                                    <select
                                        value={formData.category}
                                        onChange={(e) => setFormData(d => ({ ...d, category: e.target.value }))}
                                        className="w-full bg-background-primary border border-white/10 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-1 focus:ring-accent-primary"
                                    >
                                        {categories.map(cat => (
                                            <option key={cat} value={cat}>{cat}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="flex gap-3 justify-end pt-2">
                                    <button
                                        type="button"
                                        onClick={() => setShowForm(false)}
                                        className="px-4 py-2 text-sm text-text-secondary hover:text-text-primary hover:bg-white/5 rounded-lg"
                                    >
                                        {t('common.cancel')}
                                    </button>
                                    <button
                                        type="submit"
                                        className="px-4 py-2 text-sm bg-accent-primary hover:bg-accent-secondary text-white rounded-lg"
                                    >
                                        {editingShortcut ? t('common.save') : t('shortcuts.add')}
                                    </button>
                                </div>
                            </form>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
