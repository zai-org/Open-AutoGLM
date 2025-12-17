/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                background: {
                    primary: '#09090b', // Zinc 950
                    secondary: '#18181b', // Zinc 900
                    tertiary: '#27272a', // Zinc 800
                },
                accent: {
                    primary: '#2563eb', // Blue 600
                    secondary: '#1d4ed8', // Blue 700
                },
                text: {
                    primary: '#f4f4f5', // Zinc 100
                    secondary: '#a1a1aa', // Zinc 400
                    muted: '#71717a', // Zinc 500
                },
                status: {
                    success: '#10b981',
                    warning: '#f59e0b',
                    error: '#ef4444',
                }
            }
        },
    },
    plugins: [],
}
