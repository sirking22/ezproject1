import { createRoot } from 'react-dom/client';
import App from './App.tsx';
import './index.css';

declare global {
    interface Window { __APP_CONFIG__?: { VITE_DEMO?: string; VITE_API_URL?: string } }
}

// Inject runtime config if provided by nginx entrypoint as /config.js
if (window.__APP_CONFIG__) {
    ; (import.meta as any).env = {
        ...(import.meta as any).env,
        VITE_DEMO: window.__APP_CONFIG__!.VITE_DEMO ?? (import.meta as any).env?.VITE_DEMO,
        VITE_API_URL: window.__APP_CONFIG__!.VITE_API_URL ?? (import.meta as any).env?.VITE_API_URL,
    } as any
}

createRoot(document.getElementById("root")!).render(<App />);
