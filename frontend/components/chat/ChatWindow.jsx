import React, { useState } from 'react';
import { Send, Bot, User, Sparkles } from 'lucide-react';
import { CitationBadge } from './CitationBadge.jsx';
import { Button } from '../ui/Button.jsx';

export function ChatWindow({ messages = [], onSendMessage, isLoading, selectedDocument }) {
  const [inputQuery, setInputQuery] = useState('');
  const [useAgent, setUseAgent] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!inputQuery.trim() || isLoading) return;
    onSendMessage(inputQuery, useAgent);
    setInputQuery('');
  };

  return (
    <div className="flex flex-col h-full bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-xl">
      {/* Header */}
      <div className="p-4 border-b border-slate-800 bg-slate-800/40 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-teal-400" />
          <h2 className="text-sm font-semibold text-slate-200">
            {selectedDocument ? `Chatting with: ${selectedDocument.filename}` : 'Document Intelligence Chat'}
          </h2>
        </div>
        <span className="text-xs text-slate-500">Strictly Grounded RAG</span>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-16 text-slate-500 space-y-2">
            <Bot className="w-12 h-12 mx-auto text-slate-600" />
            <p className="text-sm">Ask any question grounded in your indexed documents.</p>
            <p className="text-xs text-slate-600">Answers will include verbatim page citations.</p>
          </div>
        ) : (
          messages.map((msg, idx) => (
            <div
              key={msg.id || idx}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role !== 'user' && (
                <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 flex-shrink-0">
                  <Bot className="w-4 h-4" />
                </div>
              )}
              <div
                className={`max-w-2xl rounded-2xl p-4 text-sm ${
                  msg.role === 'user'
                    ? 'bg-teal-600 text-white rounded-br-none'
                    : 'bg-slate-800/80 border border-slate-700 text-slate-200 rounded-bl-none'
                }`}
              >
                <p className="leading-relaxed whitespace-pre-wrap">{msg.content}</p>

                {msg.citations && msg.citations.length > 0 && (
                  <div className="mt-3 pt-2 border-t border-slate-700/60">
                    <span className="text-xs font-semibold text-teal-400 block mb-1">
                      Supporting Citations:
                    </span>
                    <div className="flex flex-wrap">
                      {msg.citations.map((c, cIdx) => (
                        <CitationBadge key={c.citation_id || cIdx} citation={c} />
                      ))}
                    </div>
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700 flex items-center justify-center text-slate-300 flex-shrink-0">
                  <User className="w-4 h-4" />
                </div>
              )}
            </div>
          ))
        )}

        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 animate-pulse">
              <Bot className="w-4 h-4" />
            </div>
            <div className="bg-slate-800/80 border border-slate-700 rounded-2xl p-4 text-slate-400 text-sm italic">
              Retrieving relevant passages and synthesizing citations...
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 border-t border-slate-800 bg-slate-900/80">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder={
              selectedDocument
                ? `Ask about ${selectedDocument.filename}...`
                : 'Ask a question across your documents...'
            }
            className="flex-1 bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-teal-500 transition-colors"
          />
          <button
            type="button"
            onClick={() => setUseAgent(!useAgent)}
            className={`px-3 py-2 text-xs font-semibold rounded-xl border flex items-center gap-1.5 transition-all ${
              useAgent
                ? 'bg-indigo-600/30 border-indigo-500 text-indigo-300 shadow-sm shadow-indigo-500/20'
                : 'bg-slate-800 border-slate-700 text-slate-400 hover:text-slate-200'
            }`}
            title="Enable multi-step autonomous agent tools"
          >
            <Sparkles className={`w-3.5 h-3.5 ${useAgent ? 'text-indigo-400' : 'text-slate-500'}`} />
            <span>Agent</span>
          </button>
          <Button type="submit" disabled={!inputQuery.trim() || isLoading}>
            <Send className="w-4 h-4 mr-1.5" />
            {useAgent ? 'Run Agent' : 'Ask'}
          </Button>
        </div>
      </form>
    </div>
  );
}

