import React, { useState, useEffect } from 'react';
import { X, Trash2, RotateCcw, AlertTriangle } from 'lucide-react';
import clsx from 'clsx';
import storage from '../services/storage';
import { useLanguage } from '../i18n/i18n.jsx';

export default function TrashModal({ isOpen, onClose, onRestored }) {
    const { t } = useLanguage();
    const [trashItems, setTrashItems] = useState([]);
    const [confirmDelete, setConfirmDelete] = useState(null);

    useEffect(() => {
        if (isOpen) {
            setTrashItems(storage.getTrash());
        }
    }, [isOpen]);

    const handleRestore = (trashId) => {
        const result = storage.restoreFromTrash(trashId);
        if (result) {
            // Re-add to history
            const history = storage.getHistory();
            history.unshift(result.item);
            storage.saveHistory(history);

            // Refresh trash list
            setTrashItems(storage.getTrash());
            onRestored?.();
        }
    };

    const handlePermanentDelete = (trashId) => {
        setConfirmDelete({
            id: trashId,
            message: t('trash.deleteConfirm')
        });
    };

    const confirmPermanentDelete = () => {
        if (confirmDelete) {
            storage.permanentlyDeleteFromTrash(confirmDelete.id);
            setTrashItems(storage.getTrash());
            setConfirmDelete(null);
        }
    };

    const handleEmptyTrash = () => {
        setConfirmDelete({
            id: 'all',
            message: t('trash.emptyTrashConfirm')
        });
    };

    const confirmEmptyTrash = () => {
        storage.emptyTrash();
        setTrashItems([]);
        setConfirmDelete(null);
    };

    const getDaysRemaining = (deletedAt) => {
        const deleted = new Date(deletedAt);
        const now = new Date();
        const daysElapsed = Math.floor((now - deleted) / (1000 * 60 * 60 * 24));
        return Math.max(0, storage.TRASH_RETENTION_DAYS - daysElapsed);
    };

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
            {/* Backdrop */}
            <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={onClose} />

            {/* Modal */}
            <div className="relative bg-background-secondary border border-white/10 rounded-xl w-full max-w-lg mx-4 shadow-2xl overflow-hidden max-h-[80vh] flex flex-col">
                {/* Header */}
                <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 shrink-0">
                    <div className="flex items-center gap-2">
                        <Trash2 size={20} className="text-text-muted" />
                        <h2 className="text-lg font-semibold text-text-primary">{t('trash.title')}</h2>
                        <span className="text-xs text-text-muted bg-background-tertiary px-2 py-0.5 rounded-full">
                            {trashItems.length}
                        </span>
                    </div>
                    <div className="flex items-center gap-2">
                        {trashItems.length > 0 && (
                            <button
                                onClick={handleEmptyTrash}
                                className="text-xs text-status-error hover:underline"
                            >
                                {t('trash.emptyTrash')}
                            </button>
                        )}
                        <button onClick={onClose} className="p-1 text-text-muted hover:text-text-primary transition-colors">
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Content */}
                <div className="flex-1 overflow-y-auto p-4 custom-scrollbar">
                    {trashItems.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-12 text-text-muted">
                            <Trash2 size={48} strokeWidth={1} className="mb-4 opacity-50" />
                            <p className="text-sm">{t('trash.empty')}</p>
                            <p className="text-xs mt-1">{t('trash.emptyDesc')}</p>
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {trashItems.map(item => (
                                <div
                                    key={item.trashId}
                                    className="bg-background-tertiary rounded-lg p-3 border border-white/5"
                                >
                                    <div className="flex items-start justify-between gap-2">
                                        <div className="flex-1 min-w-0">
                                            <div className="font-medium text-text-primary text-sm truncate">
                                                {item.task}
                                            </div>
                                            <div className="text-[10px] text-text-muted mt-1 flex items-center gap-2">
                                                <span>{new Date(item.deletedAt).toLocaleDateString()}</span>
                                                <span className="text-status-error">
                                                    {getDaysRemaining(item.deletedAt)} {t('trash.daysRemaining')}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="flex items-center gap-1 shrink-0">
                                            <button
                                                onClick={() => handleRestore(item.trashId)}
                                                className="p-1.5 text-text-muted hover:text-status-success hover:bg-status-success/10 rounded transition-colors"
                                                title={t('trash.restore')}
                                            >
                                                <RotateCcw size={14} />
                                            </button>
                                            <button
                                                onClick={() => handlePermanentDelete(item.trashId)}
                                                className="p-1.5 text-text-muted hover:text-status-error hover:bg-status-error/10 rounded transition-colors"
                                                title={t('trash.permanentDelete')}
                                            >
                                                <Trash2 size={14} />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Confirm Delete Dialog */}
                {confirmDelete && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                        <div className="bg-background-secondary border border-white/10 rounded-lg p-4 max-w-sm mx-4">
                            <div className="flex items-center gap-2 text-status-error mb-3">
                                <AlertTriangle size={20} />
                                <span className="font-semibold">{t('trash.permanentDelete')}</span>
                            </div>
                            <p className="text-sm text-text-secondary mb-4">
                                {confirmDelete.message}
                            </p>
                            <div className="flex gap-2 justify-end">
                                <button
                                    onClick={() => setConfirmDelete(null)}
                                    className="px-3 py-1.5 text-sm text-text-secondary hover:text-text-primary"
                                >
                                    {t('confirm.cancel')}
                                </button>
                                <button
                                    onClick={confirmDelete.id === 'all' ? confirmEmptyTrash : confirmPermanentDelete}
                                    className="px-3 py-1.5 text-sm bg-status-error text-white rounded hover:bg-status-error/80"
                                >
                                    {t('trash.deletePermanently')}
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
