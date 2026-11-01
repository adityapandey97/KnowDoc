import React from 'react';
import { BookOpen, ShieldCheck, Activity } from 'lucide-react';

export function Navbar({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'documents', label: 'Documents' },
    { id: 'chat', label: 'Conversational RAG' },
    { id: 'research', label: 'Deep Research' },
    { id: 'settings', label: 'Settings' }
  ];

  return (
    <header className="border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-teal-500/10 border border-teal-500/30 rounded-lg text-teal-400">
            <BookOpen className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-teal-400 to-cyan-400 bg-clip-text text-transparent">
              KnowDoc
            </h1>
            <span className="text-xs text-slate-400">AI Document Intelligence</span>
          </div>
        </div>

        <nav className="flex space-x-1 sm:space-x-2">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                activeTab === tab.id
                  ? 'bg-teal-600/20 text-teal-300 border border-teal-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>

        <div className="flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-950/60 border border-emerald-800/80 text-emerald-400 text-xs">
            <Activity className="w-3.5 h-3.5" />
            <span>Phase 1 Online</span>
          </div>
        </div>
      </div>
    </header>
  );
}

