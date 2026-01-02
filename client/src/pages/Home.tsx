import React, { useState, useRef } from "react";
import { Sidebar } from "../layouts/Sidebar";
import { animate, AnimatePresence, motion } from "framer-motion";
import { FaUpload } from "react-icons/fa6";

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'CHECK' | 'HISTORY'>('CHECK');
  const [isSnapping, setIsSnapping] = useState(true);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const isNavigating = useRef(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const checkRef = useRef<HTMLDivElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleNavigate = (target: 'CHECK' | 'HISTORY') => {
    isNavigating.current = true;
    const targetRef = target === 'CHECK' ? checkRef : historyRef;
    const container = containerRef.current;

    if (container && targetRef.current) {
      setIsSnapping(false);

      const top = targetRef.current.offsetTop;

      animate(container.scrollTop, top, {
        type: "tween",
        duration: 0.8,
        ease: "easeInOut",
        onUpdate: (latest) => {
          container.scrollTop = latest;
        },
        onComplete: () => {
          setIsSnapping(true);
          setTimeout(() => {
            isNavigating.current = false;
          }, 100);
        }
      });
    }
    setActiveTab(target);
  };

  const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
    if (isNavigating.current) return;

    const { scrollTop, offsetHeight } = e.currentTarget;
    if (scrollTop > offsetHeight / 2) {
      setActiveTab('HISTORY');
    } else {
      setActiveTab('CHECK');
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (previewUrl){
        URL.revokeObjectURL(previewUrl);
      }
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className={`h-dvh overflow-y-auto bg-linear-to-t no-scrollbar from-background from-0% to-[#242323] bg-local ${isSnapping ? 'snap-y snap-mandatory' : ''}`}
    >

      <Sidebar activeTab={activeTab} onNavigate={handleNavigate} />

      <div className="fixed h-full w-16 md:w-24 xl:w-32 flex items-center justify-center pointer-events-none z-10">
        <div className="rotate-180 [writing-mode:vertical-lr] flex items-center justify-center">
          <AnimatePresence mode='wait'>
            <motion.h2
              key={activeTab}
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -40 }}
              transition={{ duration: 0.4, ease: "easeInOut" }}
              className="font-heading font-black text-4xl text-highlight/80 tracking-tighter uppercase whitespace-nowrap md:text-5xl xl:text-6xl"
            >
              {activeTab === 'CHECK' ? 'Anomaly Check' : 'Anomaly History'}
            </motion.h2>
          </AnimatePresence>
        </div>
      </div>

      <section
        ref={checkRef}
        className="h-dvh w-full flex items-center justify-center pl-18 pr-18 md:pl-24 md:pr-24 xl:pl-32 xl:pr-32 snap-start"
      >
        <div className="w-full md:max-w-lg max-w-sm">
          <div className="bg-card aspect-square rounded-md border border-text/20 flex items-center justify-center group cursor-pointer p-4"
          onClick={() => fileInputRef.current?.click()}>
            <div className="w-full h-full border-dashed p-0.5 border sm:border-2 border-text/50 rounded-md group-hover:border-highlight/60 duration-300 transition-colors flex items-center justify-center">
              <input 
                type="file"
                ref={fileInputRef}
                onChange={handleFileChange}
                accept=".jpg, .jpeg, .png, .bmp"
                className="hidden" 
              />
              {previewUrl ? (
                <motion.img 
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ 
                    duration: 0.3,
                    ease: "easeInOut"
                  }}
                  src={previewUrl} 
                  className="w-full h-full object-cover rounded-sm"
                  alt="Preview"
                />
              ) : (
                <div className="flex flex-col items-center gap-4">
                  <FaUpload className="text-text/50 text-xl sm:text-4xl group-hover:text-highlight/60 transition-colors duration-300" />
                  <span className="text-text/50 text-xs sm:text-sm md:text-xl uppercase tracking-widest font-sans group-hover:text-highlight/60 duration-300">
                    Upload Image
                  </span>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      <section
        ref={historyRef}
        className="h-dvh w-full flex items-center justify-center pl-18 pr-18 md:pl-24 md:pr-24 xl:pl-32 xl:pr-32 snap-start"
      >
        <div className="w-full max-w-5xl">
          <div className="grid grid-cols-2 gap-8 w-full">
            <div className="h-48 bg-primary rounded-sm border border-zinc-800 flex items-center justify-center">
              <span className="text-zinc-700 font-mono text-xs italic">Record_001.data</span>
            </div>
            <div className="h-48 bg-primary rounded-sm border border-zinc-800 flex items-center justify-center">
              <span className="text-zinc-700 font-mono text-xs italic">Record_002.data</span>
            </div>
          </div>
        </div>
      </section>

    </div>
  );
};

export default Home;