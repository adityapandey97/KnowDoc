import React from 'react';

export function Badge({ status, label }) {
  const statusStyles = {
    ready: 'bg-emerald-950 text-emerald-400 border-emerald-800',
    processing: 'bg-blue-950 text-blue-400 border-blue-800 animate-pulse',
    chunked: 'bg-indigo-950 text-indigo-400 border-indigo-800',
    embedding: 'bg-purple-950 text-purple-400 border-purple-800 animate-pulse',
    pending: 'bg-amber-950 text-amber-400 border-amber-800',
    failed: 'bg-rose-950 text-rose-400 border-rose-800'
  };

  const style = statusStyles[status?.toLowerCase()] || 'bg-slate-800 text-slate-300 border-slate-700';

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium border ${style}`}>
      {label || status}
    </span>
  );
}

