import React from 'react';
import { FileText, Trash2, Calendar, Layers } from 'lucide-react';
import { Badge } from '../ui/Badge.jsx';
import { formatBytes, formatDate } from '../../utils/formatters.js';

export function DocumentList({ documents, onDelete, onSelect, selectedId }) {
  if (!documents || documents.length === 0) {
    return (
      <div className="text-center py-12 border border-slate-800 rounded-xl bg-slate-800/20">
        <FileText className="w-10 h-10 text-slate-500 mx-auto mb-2" />
        <p className="text-slate-400 text-sm">No documents in your library yet.</p>
        <p className="text-slate-500 text-xs mt-1">Upload a PDF above to begin indexing.</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {documents.map((doc) => (
        <div
          key={doc.id}
          onClick={() => onSelect && onSelect(doc)}
          className={`flex items-center justify-between p-4 rounded-xl border transition-all cursor-pointer ${
            selectedId === doc.id
              ? 'bg-teal-950/30 border-teal-800 shadow-md'
              : 'bg-slate-800/40 border-slate-800 hover:bg-slate-800/70 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center gap-3 min-w-0">
            <div className="p-2 bg-slate-800 border border-slate-700 rounded-lg text-teal-400 flex-shrink-0">
              <FileText className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <h3 className="text-sm font-medium text-slate-200 truncate">{doc.filename}</h3>
              <div className="flex items-center gap-3 text-xs text-slate-400 mt-1">
                <span>{formatBytes(doc.sizeBytes)}</span>
                {doc.pageCount > 0 && (
                  <span className="flex items-center gap-1">
                    <Layers className="w-3 h-3" /> {doc.pageCount} pages ({doc.chunkCount} chunks)
                  </span>
                )}
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" /> {formatDate(doc.createdAt)}
                </span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <Badge status={doc.status} />
            {onDelete && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(doc.id);
                }}
                className="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/30 rounded-lg transition-colors"
                title="Delete document"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

