import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { IoClose } from 'react-icons/io5';

interface AnomalyData {
    _id: string;
    videoName: string;
    originalUrl: string;
    isAnomaly: boolean;
    accuracy: number;
    createdAt: string;
}

interface VideoModalProps {
    isOpen: boolean;
    onClose: () => void;
    data: AnomalyData | null;
}

const VideoModal: React.FC<VideoModalProps> = ({ isOpen, onClose, data }) => {
    if (!isOpen || !data) return null;

    const videoSrc = `${data.originalUrl}`;

    return (
        <AnimatePresence>
            {isOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        exit={{ opacity: 0 }}
                        onClick={onClose}
                        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                    />

                    <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: 20 }}
                        transition={{ duration: 0.3, ease: 'easeOut' }}
                        className="relative w-full max-w-sm bg-card rounded-xl border border-text/20 overflow-hidden shadow-2xl z-10"
                    >
                        <div className="w-full flex items-center justify-between p-4 border-b border-text/20">
                            <div className="flex items-center gap-2">
                                <span className="text-text/60 text-xs uppercase tracking-widest"></span>
                                <div className="flex items-center gap-2 pointer-events-none">
                                    <div className={`w-2 h-2 rounded-full shadow-[0_0_8px] ${data.isAnomaly ? 'bg-error shadow-error' : 'bg-success shadow-success'}`}></div>
                                    <span className={`font-heading font-bold tracking-wider text-sm ${data.isAnomaly ? 'text-error' : 'text-success'}`}>
                                        {data.isAnomaly ? 'ANOMALY' : 'NORMAL'}
                                    </span>
                                </div>
                            </div>

                            <button
                                onClick={onClose}
                                className="text-text/60 hover:text-highlight duration-300 cursor-pointer transition-colors"
                            >
                                <IoClose size={24} />
                            </button>
                        </div>
                        <div className="aspect-square w-full bg-black/40 relative">
                            <video
                                src={videoSrc}
                                controls
                                className="absolute inset-0 w-full h-full object-contain"
                            />
                        </div>
                        <div className="p-4 flex items-center justify-between bg-card border-t border-text/20">
                            <div className="flex flex-col">
                                <span className="text-text/60 text-[10px] uppercase tracking-wider">Accuracy</span>
                                <span className="text-text font-mono text-lg font-bold">{(Number(data.accuracy)|| 0).toFixed(1)}%</span>
                            </div>
                            <div className="flex flex-col items-end">
                                <span className="text-text/60 text-[10px] uppercase tracking-wider">Date</span>
                                <span className="text-text/80 text-xs mt-0.5">
                                    {new Date(data.createdAt).toLocaleString(undefined, {
                                        month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                                    })}
                                </span>
                            </div>
                        </div>

                    </motion.div>
                </div>
            )}
        </AnimatePresence>
    );
};

export default VideoModal;
