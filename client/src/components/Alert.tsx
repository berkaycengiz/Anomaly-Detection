import React, { useEffect } from 'react';
import { motion } from 'framer-motion';
import { IoCheckmarkCircle, IoWarning, IoInformationCircle, IoCloseCircle, IoClose } from 'react-icons/io5';

export type AlertType = 'success' | 'error' | 'warning' | 'info';

export interface AlertProps {
    id: string;
    type: AlertType;
    message: string;
    duration?: number;
    onClose: (id: string) => void;
}

const alertVariants = {
    initial: { opacity: 0, y: 50, scale: 0.9 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, scale: 0.9, transition: { duration: 0.2 } }
};

const getIcon = (type: AlertType) => {
    switch (type) {
        case 'success': return <IoCheckmarkCircle className="text-green-500 text-xl" />;
        case 'error': return <IoCloseCircle className="text-red-500 text-xl" />;
        case 'warning': return <IoWarning className="text-yellow-500 text-xl" />;
        case 'info': return <IoInformationCircle className="text-blue-500 text-xl" />;
    }
};

const getBorderColor = (type: AlertType) => {
    switch (type) {
        case 'success': return 'border-green-500/50';
        case 'error': return 'border-red-500/50';
        case 'warning': return 'border-yellow-500/50';
        case 'info': return 'border-blue-500/50';
    }
}

const Alert: React.FC<AlertProps> = ({ id, type, message, duration = 3000, onClose }) => {
    useEffect(() => {
        if (duration > 0) {
            const timer = setTimeout(() => {
                onClose(id);
            }, duration);
            return () => clearTimeout(timer);
        }
    }, [id, duration, onClose]);

    return (
        <motion.div
            layout
            variants={alertVariants}
            initial="initial"
            animate="animate"
            exit="exit"
            className={`relative flex items-center gap-3 p-4 rounded-lg bg-[#1a1a1a] border ${getBorderColor(type)} shadow-lg backdrop-blur-md min-w-[300px] max-w-sm pointer-events-auto`}
        >
            <div className="shrink-0">
                {getIcon(type)}
            </div>
            <div className="flex-1 mr-2">
                <p className="text-sm font-medium text-white/90 leading-snug">
                    {message}
                </p>
            </div>
            <button
                onClick={() => onClose(id)}
                className="text-white/40 hover:text-white transition-colors"
            >
                <IoClose size={18} />
            </button>
        </motion.div>
    );
};

export default Alert;
