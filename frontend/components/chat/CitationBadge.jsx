import React, { useState } from 'react';
import { Bookmark, ExternalLink } from 'lucide-react';

export function CitationBadge({ citation }) {
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div className="relative inline-block my-1 mr-2">
      <button
        onClick={() => setShowTooltip(!showTooltip)}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded bg-teal-950/80 border border-teal-800 text-teal-300 text-xs hover:bg-teal-900/90 transition-colors"
      >
        <Bookmark className="w-3 h-3 text-teal-400" />
        <span>Page {citation.page_number || citation.pageNumber}</span>
      </button>

      {showTooltip && (
        <div className="absolute bottom-full left-0 mb-2 w-72 p-3 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl z-50 text-xs text-slate-300 backdrop-blur">
          <div className="flex items-center justify-between pb-1.5 mb-1.5 border-b border-slate-800 text-teal-400 font-semibold">
            <span>Citation Evidence</span>
            <span>Page {citation.page_number || citation.pageNumber}</span>
          </div>
          <p className="italic text-slate-300 leading-relaxed">
            "{citation.excerpt}"
          </p>
        </div>
      )}
    </div>
  );
}

