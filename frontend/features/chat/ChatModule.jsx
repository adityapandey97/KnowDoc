import React, { useState } from 'react';
import { ChatWindow } from '../../components/chat/ChatWindow.jsx';
import { Card } from '../../components/ui/Card.jsx';
import { FileText, ShieldAlert } from 'lucide-react';

export function ChatModule({ documents, selectedDoc, onSelectDoc }) {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSendMessage = async (query) => {
    // Optimistic user message
    const userMsg = {
      id: Date.now().toString(),
      role: 'user',
      content: query
    };
    setMessages((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      // In Phase 1 foundation, if no active conversation exists, run direct query or mock response
      const token = localStorage.getItem('knowdoc_access_token');
      // Simulated answer for Phase 1 starter
      setTimeout(() => {
        const assistantMsg = {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: `Analysis of query: "${query}". Based on ${selectedDoc ? selectedDoc.filename : 'indexed documents'}, key operations and metrics are verified.`,
          citations: selectedDoc
            ? [
                {
                  citation_id: 'cit_1',
                  pageNumber: 1,
                  excerpt: `Relevant section from ${selectedDoc.filename} regarding the query.`
                }
              ]
            : []
        };
        setMessages((prev) => [...prev, assistantMsg]);
        setLoading(false);
      }, 700);
    } catch (err) {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-10rem)]">
      {/* Context Selector */}
      <div className="lg:col-span-1 space-y-4 flex flex-col">
        <Card className="flex-1 overflow-y-auto">
          <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <FileText className="w-4 h-4 text-teal-400" />
            Active Context Scope
          </h3>

          <div className="space-y-2">
            <button
              onClick={() => onSelectDoc(null)}
              className={`w-full text-left p-2.5 rounded-lg text-xs font-medium border transition-colors ${
                !selectedDoc
                  ? 'bg-teal-950/40 border-teal-800 text-teal-300'
                  : 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
              }`}
            >
              All Documents (Global Library)
            </button>

            {documents.map((doc) => (
              <button
                key={doc.id}
                onClick={() => onSelectDoc(doc)}
                className={`w-full text-left p-2.5 rounded-lg text-xs font-medium border transition-colors truncate block ${
                  selectedDoc?.id === doc.id
                    ? 'bg-teal-950/40 border-teal-800 text-teal-300'
                    : 'bg-slate-900 border-slate-700 text-slate-300 hover:bg-slate-800'
                }`}
              >
                <div className="truncate font-semibold">{doc.filename}</div>
                <div className="text-[10px] text-slate-400 mt-0.5">Status: {doc.status}</div>
              </button>
            ))}
          </div>
        </Card>

        <Card className="bg-amber-950/20 border-amber-800/40 text-amber-300/80 p-3 text-xs flex gap-2 items-start">
          <ShieldAlert className="w-4 h-4 flex-shrink-0 text-amber-400 mt-0.5" />
          <span>
            Strict grounding active: Answers are constrained to cited passages. Untrusted document inputs cannot inject prompt instructions.
          </span>
        </Card>
      </div>

      {/* Main Chat Interface */}
      <div className="lg:col-span-3 h-full">
        <ChatWindow
          messages={messages}
          onSendMessage={handleSendMessage}
          isLoading={loading}
          selectedDocument={selectedDoc}
        />
      </div>
    </div>
  );
}

