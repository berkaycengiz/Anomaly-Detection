import React, { useState, useRef } from "react";
import { Sidebar } from "../layouts/Sidebar";
import { animate, AnimatePresence, motion } from "framer-motion";

const Home: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'CHECK' | 'HISTORY'>('CHECK');
  const [isSnapping, setIsSnapping] = useState(true);

  const isNavigating = useRef(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const checkRef = useRef<HTMLDivElement>(null);
  const historyRef = useRef<HTMLDivElement>(null);

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
        <div className="w-full max-w-5xl">
          <div className="bg-primary aspect-video rounded-sm border border-zinc-800 shadow-2xl flex items-center justify-center relative group">
            <div className="absolute inset-4 border border-dashed border-zinc-800 rounded-sm group-hover:border-highlight/30 transition-colors"></div>
            <p className="text-text font-body uppercase tracking-[0.3em] text-xs">Drop wood sample here</p>
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