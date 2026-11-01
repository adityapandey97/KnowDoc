import React from 'react';

export function Card({ children, className = '', ...props }) {
  return (
    <div
      className={`bg-slate-800/80 border border-slate-700/80 rounded-xl shadow-lg p-5 backdrop-blur-sm ${className}`}
      {...props}
    >
      {children}
    </div>
  );
}

