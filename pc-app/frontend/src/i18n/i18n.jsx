import React, { createContext, useContext, useState, useEffect } from 'react';
import zhCN from './locales/zh-CN';
import enUS from './locales/en-US';

// Available locales
export const LOCALES = {
    'zh-CN': { name: '简体中文', translations: zhCN },
    'en-US': { name: 'English', translations: enUS },
};

const STORAGE_KEY = 'aiphone_language';

// Create context
const LanguageContext = createContext(null);

// Get nested value from object using dot notation
const getNestedValue = (obj, path) => {
    return path.split('.').reduce((current, key) => {
        return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
};

// Language Provider component
export function LanguageProvider({ children }) {
    const [locale, setLocale] = useState(() => {
        // Try to get saved language preference
        const saved = localStorage.getItem(STORAGE_KEY);
        if (saved && LOCALES[saved]) {
            return saved;
        }
        // Default to Chinese
        return 'zh-CN';
    });

    // Save language preference when it changes
    useEffect(() => {
        localStorage.setItem(STORAGE_KEY, locale);
    }, [locale]);

    // Translation function
    const t = (key, params = {}) => {
        const translations = LOCALES[locale]?.translations || zhCN;
        let value = getNestedValue(translations, key);

        // Fallback to Chinese if key not found
        if (value === undefined) {
            value = getNestedValue(zhCN, key);
        }

        // Still not found, return key
        if (value === undefined) {
            console.warn(`Translation key not found: ${key}`);
            return key;
        }

        // Replace parameters like {task} with actual values
        if (typeof value === 'string' && Object.keys(params).length > 0) {
            Object.entries(params).forEach(([paramKey, paramValue]) => {
                value = value.replace(new RegExp(`\\{${paramKey}\\}`, 'g'), paramValue);
            });
        }

        return value;
    };

    // Toggle between languages
    const toggleLanguage = () => {
        setLocale(prev => prev === 'zh-CN' ? 'en-US' : 'zh-CN');
    };

    const value = {
        locale,
        setLocale,
        t,
        toggleLanguage,
        isEnglish: locale === 'en-US',
        isChinese: locale === 'zh-CN',
    };

    return (
        <LanguageContext.Provider value={value}>
            {children}
        </LanguageContext.Provider>
    );
}

// Custom hook to use language context
export function useLanguage() {
    const context = useContext(LanguageContext);
    if (!context) {
        throw new Error('useLanguage must be used within a LanguageProvider');
    }
    return context;
}

export default { LanguageProvider, useLanguage, LOCALES };
