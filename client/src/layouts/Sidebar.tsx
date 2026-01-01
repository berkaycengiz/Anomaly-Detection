import { motion } from "framer-motion";
import { FaSearch } from "react-icons/fa";
import { FaHistory } from "react-icons/fa";
import { useState } from "react";

interface SidebarProps {
  activeTab: 'CHECK' | 'HISTORY';
  onNavigate: (target: 'CHECK' | 'HISTORY') => void;
}

export const Sidebar = ({ activeTab, onNavigate }: SidebarProps) => {

  const [isAnimating, setIsAnimating] = useState(false);

  return (
    <aside className="fixed w-18 md:w-24 xl:w-32 h-full top-0 right-0 flex flex-col items-center justify-center z-50">
      
      <div className="relative w-12 h-36 md:w-14 md:h-48 bg-card/40 backdrop-blur-xl rounded-full flex flex-col border border-text/20">
        
        <motion.div
          animate={{ y: activeTab === 'CHECK' ? '0%' : '100%' }}
          transition={{ type: "tween", duration: 0.8 }}
          onAnimationStart={() => setIsAnimating(true)}
          onAnimationComplete={() => setIsAnimating(false)}
          className="absolute w-full h-[calc(50%)] bg-highlight/80 rounded-full border-2 border-highlight shadow-[0_0_20px] shadow-highlight/70"
        />
        <button 
          onClick={() => onNavigate('CHECK')}
          disabled={isAnimating === true}
          className="flex-1 z-10 w-full flex items-center justify-center relative cursor-pointer"
        >
          <FaSearch className={`transition-colors duration-600 ${activeTab === 'CHECK' ? 'text-white' : 'text-white/20'}`}></FaSearch>
        </button>

        <button 
          onClick={() => onNavigate('HISTORY')}
          disabled={isAnimating === true}
          className="flex-1 z-10 w-full flex items-center justify-center relative cursor-pointer"
        >
          <FaHistory className={`transition-colors duration-600 ${activeTab === 'HISTORY' ? 'text-white' : 'text-white/20'}`}></FaHistory>
        </button>

      </div>
    </aside>
  );
};