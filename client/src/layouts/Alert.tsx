import React, { createContext, useContext, useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { AnimatePresence } from 'framer-motion';
import Alert from '../components/Alert';
import type { AlertType } from '../components/Alert';

interface AlertData {
    id: string;
    type: AlertType;
    message: string;
    duration?: number;
}

interface AlertContextType {
    showAlert: (message: string, type: AlertType, duration?: number) => void;
    removeAlert: (id: string) => void;
}

const AlertContext = createContext<AlertContextType | undefined>(undefined);

export const useAlert = () => {
    const context = useContext(AlertContext);
    if (!context) {
        throw new Error('useAlert must be used within an AlertProvider');
    }
    return context;
};

export const AlertProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [alerts, setAlerts] = useState<AlertData[]>([]);

    const showAlert = useCallback((message: string, type: AlertType, duration = 3000) => {
        const id = Math.random().toString(36).substr(2, 9);
        setAlerts((prev) => [...prev, { id, message, type, duration }]);
    }, []);

    const removeAlert = useCallback((id: string) => {
        setAlerts((prev) => prev.filter((alert) => alert.id !== id));
    }, []);

    return (
        <AlertContext.Provider value={{ showAlert, removeAlert }}>
            {children}
            <div className="fixed top-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
                <AnimatePresence mode='popLayout'>
                    {alerts.map((alert) => (
                        <Alert
                            key={alert.id}
                            {...alert}
                            onClose={removeAlert}
                        />
                    ))}
                </AnimatePresence>
            </div>
        </AlertContext.Provider>
    );
};
