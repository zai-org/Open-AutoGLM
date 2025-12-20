import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Terminal, Brain, Zap, CheckCircle, AlertCircle, MessageSquare, Trash2, ArrowUp } from 'lucide-react';
import clsx from 'clsx';
import { useLanguage } from '../../i18n/i18n.jsx';

// --- Sub-components for different log types ---

const LogTimestamp = ({ time }) => (
    <span className="text-[11px] text-text-muted font-mono shrink-0 pt-1 select-none">
        [{time}]
    </span>
);

const ThinkingLog = ({ content }) => (
    <div className="flex gap-2 text-text-muted italic bg-background-tertiary/30 p-2 rounded border border-transparent hover:border-text-muted/20 transition-colors">
        <Brain size={14} className="mt-1 shrink-0 opacity-70" />
        <span className="whitespace-pre-wrap text-[13px]">{content}</span>
    </div>
);

const ActionLog = ({ content, t }) => {
    let displayContent = content;
    if (typeof content === 'object') {
        displayContent = JSON.stringify(content, null, 2);
    }

    return (
        <div className="flex gap-2 text-text-primary bg-background-tertiary p-2 rounded border border-white/5">
            <Zap size={14} className="mt-1 shrink-0 text-accent-primary" />
            <div className="flex-1 overflow-hidden">
                <div className="text-[11px] text-text-muted uppercase font-bold mb-1">{t('log.executeAction')}</div>
                <pre className="text-[12px] font-mono text-accent-primary whitespace-pre-wrap overflow-x-auto">
                    {displayContent}
                </pre>
            </div>
        </div>
    );
};

const ModelResponseLog = ({ content, t }) => (
    <div className="flex flex-col my-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
        <div className="flex items-center gap-2 mb-1 px-1">
            <div className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-400 flex items-center justify-center border border-cyan-500/30">
                <MessageSquare size={12} />
            </div>
            <span className="text-xs font-bold text-cyan-400">{t('log.modelResponse')}</span>
        </div>
        <div className="bg-cyan-950/20 border-l-2 border-cyan-500 rounded-r-md p-3 ml-2.5">
            <div className="prose prose-invert prose-sm max-w-none text-cyan-100/90 text-[13px] leading-relaxed break-words whitespace-pre-wrap">
                <ReactMarkdown>{content}</ReactMarkdown>
            </div>
        </div>
    </div>
);

const PerformanceLog = ({ content }) => (
    <div className="font-mono text-[11px] text-amber-400 bg-amber-950/30 border border-amber-900/50 p-2 rounded inline-block whitespace-pre">
        {content}
    </div>
);

const ErrorLog = ({ content }) => (
    <div className="flex gap-2 text-status-error font-bold bg-status-error/10 p-2 rounded border border-status-error/20">
        <AlertCircle size={16} className="mt-0.5 shrink-0" />
        <span>{content}</span>
    </div>
);

const SuccessLog = ({ content }) => (
    <div className="flex gap-2 text-status-success font-bold bg-status-success/10 p-2 rounded border border-status-success/20">
        <CheckCircle size={16} className="mt-0.5 shrink-0" />
        <span>{content}</span>
    </div>
);

const ApiLog = ({ content }) => {
    // Safety check for undefined content
    if (!content) return null;

    // We can collapse this or show minimal info
    const direction = content.direction === 'request' ? '>> Request' : '<< Response';

    return (
        <details className="group">
            <summary className="flex items-center gap-2 text-[11px] text-purple-400 cursor-pointer hover:text-purple-300 select-none">
                <span className="opacity-70 font-mono">{direction}</span>
                <span className="text-[10px] bg-purple-900/30 px-1 rounded opacity-0 group-hover:opacity-100 transition-opacity">Details</span>
            </summary>
            <pre className="mt-1 text-[10px] text-purple-200/70 bg-background-tertiary p-2 rounded overflow-x-auto max-h-32">
                {JSON.stringify(content.content, null, 2)}
            </pre>
        </details>
    );
}


// --- Main Viewer Component ---

const LogItem = React.memo(({ step, onDelete, t }) => {
    const { type, content, timestamp, error, message } = step;

    // Resolve actual content text/object
    const actualContent = content || message || error || '';

    const renderContent = () => {
        switch (type) {
            case 'model_response':
                return <ModelResponseLog content={actualContent} t={t} />;
            case 'thinking':
                return <ThinkingLog content={actualContent} />;
            case 'action':
                return <ActionLog content={actualContent} t={t} />;
            case 'performance':
                return <PerformanceLog content={actualContent} />;
            case 'error':
                return <ErrorLog content={actualContent} />;
            case 'success':
            case 'complete': // Handle 'complete' as success
                return <SuccessLog content={actualContent} />;
            case 'api_log':
                return <ApiLog content={actualContent} />;
            case 'raw_log':
                return <div className="text-[10px] text-text-tertiary font-mono whitespace-pre-wrap opacity-40 ml-6">{actualContent}</div>;
            case 'thinking_start':
                return <div className="text-[11px] text-text-muted italic ml-6">{t('log.thinking')}</div>;
            case 'start':
                return <div className="text-xs text-accent-primary font-bold border-b border-accent-primary/20 pb-1 mb-2">{t('log.taskStart')} {step.task}</div>;
            case 'user_message':
                return (
                    <div className="flex flex-col my-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="flex items-center gap-2 mb-1 px-1">
                            <div className="w-5 h-5 rounded-full bg-blue-500/20 text-blue-400 flex items-center justify-center border border-blue-500/30">
                                <span className="text-[10px] font-bold">{t('log.me')}</span>
                            </div>
                            <span className="text-xs font-bold text-blue-400">{t('log.user')}</span>
                        </div>
                        <div className="bg-blue-950/20 border-l-2 border-blue-500 rounded-r-md p-3 ml-2.5">
                            <div className="text-blue-100/90 text-[13px] leading-relaxed whitespace-pre-wrap">{actualContent}</div>
                        </div>
                    </div>
                );
            case 'assistant_message':
                return (
                    <div className="flex flex-col my-2 animate-in fade-in slide-in-from-bottom-2 duration-300">
                        <div className="flex items-center gap-2 mb-1 px-1">
                            <div className="w-5 h-5 rounded-full bg-green-500/20 text-green-400 flex items-center justify-center border border-green-500/30">
                                <span className="text-[10px] font-bold">AI</span>
                            </div>
                            <span className="text-xs font-bold text-green-400">{t('log.assistant')}</span>
                        </div>
                        <div className="bg-green-950/20 border-l-2 border-green-500 rounded-r-md p-3 ml-2.5">
                            <div className="prose prose-invert prose-sm max-w-none text-green-100/90 text-[13px] leading-relaxed">
                                <ReactMarkdown>{actualContent}</ReactMarkdown>
                            </div>
                        </div>
                    </div>
                );
            default:
                return <div className="text-text-secondary whitespace-pre-wrap ml-6">{typeof actualContent === 'string' ? actualContent : JSON.stringify(actualContent)}</div>;
        }
    };

    return (
        <div className="relative flex gap-2 py-1 hover:bg-white/5 px-2 -mx-2 rounded transition-colors group">
            <LogTimestamp time={timestamp} />
            <div className="flex-1 min-w-0 overflow-hidden">
                {renderContent()}
            </div>
            {onDelete && (
                <button
                    onClick={() => onDelete()}
                    className="absolute right-2 top-2 p-1 bg-background-secondary rounded text-text-muted hover:text-status-error opacity-0 group-hover:opacity-100 transition-opacity"
                    title={t('log.deleteMessage')}
                >
                    <Trash2 size={12} />
                </button>
            )}
        </div>
    );
});

export default function LogViewer({ logs, autoScroll = true, onDeleteStep }) {
    const { t } = useLanguage();
    const containerRef = React.useRef(null);
    const endRef = React.useRef(null);
    const prevLogsLengthRef = React.useRef(0);

    // Auto-scroll effect: scroll to bottom when logs update
    React.useEffect(() => {
        if (endRef.current) {
            // Always scroll to bottom on first load (when logs length changes from 0 to > 0)
            // or when autoScroll is enabled
            const isFirstLoad = prevLogsLengthRef.current === 0 && logs && logs.length > 0;
            if (isFirstLoad || autoScroll) {
                endRef.current.scrollIntoView({ behavior: isFirstLoad ? 'auto' : 'smooth' });
            }
        }
        prevLogsLengthRef.current = logs?.length || 0;
    }, [logs, autoScroll]);

    if (!logs || logs.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-text-muted opacity-50 space-y-4">
                <Terminal size={48} strokeWidth={1} />
                <p className="text-sm">{t('log.ready')}</p>
            </div>
        );
    }

    const scrollToTop = () => {
        containerRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
    };

    return (
        <div className="relative h-full">
            <div
                ref={containerRef}
                className="h-full overflow-y-auto custom-scrollbar"
            >
                <div className="flex flex-col gap-0.5 p-4 pb-20">
                    {logs.map((step, index) => (
                        <LogItem
                            key={index}
                            step={step}
                            onDelete={onDeleteStep ? () => onDeleteStep(index) : null}
                            t={t}
                        />
                    ))}
                    <div ref={endRef} />
                </div>
            </div>

            {/* Floating scroll to top button */}
            <button
                onClick={scrollToTop}
                className="absolute bottom-6 right-6 w-10 h-10 bg-accent-primary hover:bg-accent-secondary text-white rounded-full shadow-lg shadow-accent-primary/30 flex items-center justify-center transition-all hover:scale-110"
                title={t('log.scrollToTop')}
            >
                <ArrowUp size={18} />
            </button>
        </div>
    );
}
