interface SidebarProps {
  activeTab: 'CHECK' | 'HISTORY';
  onNavigate: (target: 'CHECK' | 'HISTORY') => void;
}

export const Sidebar = ({ activeTab, onNavigate }: SidebarProps) => {
  return (
    <aside className="fixed right-0 top-0 h-full w-20 bg-primary/50 backdrop-blur-xl border-l border-zinc-800 flex flex-col items-center justify-center gap-12 z-50">
      <button 
        onClick={() => onNavigate('CHECK')}
        className="group relative flex items-center justify-center p-4"
      >
        <span className="absolute right-full mr-4 text-[10px] font-mono tracking-widest opacity-0 group-hover:opacity-100 transition-opacity text-highlight">SCANNER</span>
        <div className={`w-3 h-3 rounded-full transition-all duration-500 ${activeTab === 'CHECK' ? 'bg-highlight shadow-[0_0_15px_#F59E0B]' : 'bg-zinc-700'}`}></div>
      </button>

      <button 
        onClick={() => onNavigate('HISTORY')}
        className="group relative flex items-center justify-center p-4"
      >
        <span className="absolute right-full mr-4 text-[10px] font-mono tracking-widest opacity-0 group-hover:opacity-100 transition-opacity text-secondary">DATABASE</span>
        <div className={`w-3 h-3 rounded-full transition-all duration-500 ${activeTab === 'HISTORY' ? 'bg-secondary shadow-[0_0_15px_#B4A8FA]' : 'bg-zinc-700'}`}></div>
      </button>
    </aside>
  );
};