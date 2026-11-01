import React from 'react';
import { FileText, MessageSquare, Plus, RefreshCw } from 'lucide-react';

export function Sidebar({ documents = [], conversations = [], onNewChat, activeDocId }) {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/60 p-4 flex flex-col gap-6 hidden md:flex">
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <FileText className="w-3.5 h-3.5" />
            Library ({documents.length})
          </h2>
        </div>
        <div className="space-y-1.5 max-h-56 overflow-y-auto pr-1">
          {documents.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No documents indexed</p>
          ) : (
            documents.map((doc) => (
              <div
                key={doc.id}
                className={`p-2 rounded-lg text-xs truncate flex items-center justify-between border ${
                  activeDocId === doc.id
                    ? 'bg-teal-950/40 border-teal-800 text-teal-300'
                    : 'bg-slate-800/40 border-slate-800 text-slate-300 hover:bg-slate-800'
                }`}
              >
                <span className="truncate">{doc.filename}</span>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="flex-1 flex flex-col">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider flex items-center gap-1.5">
            <MessageSquare className="w-3.5 h-3.5" />
            Recent Chats
          </h2>
          <button
            onClick={onNewChat}
            className="p-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs flex items-center gap-1"
            title="Start New Conversation"
          >
            <Plus className="w-3 h-3" />
          </button>
        </div>

        <div className="space-y-1.5 overflow-y-auto flex-1">
          {conversations.length === 0 ? (
            <p className="text-xs text-slate-500 italic">No conversations yet</p>
          ) : (
            conversations.map((c) => (
              <div
                key={c.id}
                className="p-2 rounded-lg text-xs bg-slate-800/40 border border-slate-800 text-slate-300 hover:bg-slate-800 cursor-pointer truncate"
              >
                {c.title}
              </div>
            ))
          )}
        </div>
      </div>
    </aside>
  );
}

