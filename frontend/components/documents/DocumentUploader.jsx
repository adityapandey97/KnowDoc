import React, { useState } from 'react';
import { UploadCloud, File, AlertCircle, CheckCircle } from 'lucide-react';
import { Button } from '../ui/Button.jsx';
import { formatBytes } from '../../utils/formatters.js';

export function DocumentUploader({ onUploadSuccess }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const MAX_SIZE_MB = 25;
  const MAX_BYTES = MAX_SIZE_MB * 1024 * 1024;

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const validateAndSetFile = (file) => {
    setError(null);
    setSuccess(null);

    if (!file) return;

    if (file.type !== 'application/pdf' && !file.name.toLowerCase().endsWith('.pdf')) {
      setError('Invalid file type. Only PDF documents are supported.');
      return;
    }

    if (file.size > MAX_BYTES) {
      setError(`File size exceeds the ${MAX_SIZE_MB} MB limit.`);
      return;
    }

    setSelectedFile(file);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndSetFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e) => {
    if (e.target.files && e.target.files[0]) {
      validateAndSetFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;

    setUploading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);

      const res = await fetch('/api/v1/documents', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${localStorage.getItem('knowdoc_access_token') || ''}`
        },
        body: formData
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data?.error?.message || 'Upload failed');
      }

      setSuccess(`Document "${selectedFile.name}" queued for ingestion!`);
      setSelectedFile(null);
      if (onUploadSuccess) onUploadSuccess(data.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all ${
          dragActive
            ? 'border-teal-500 bg-teal-500/10'
            : 'border-slate-700 bg-slate-800/40 hover:border-slate-600'
        }`}
      >
        <UploadCloud className="w-12 h-12 text-slate-400 mx-auto mb-3" />
        <p className="text-sm font-medium text-slate-200">
          Drag and drop your PDF here, or{' '}
          <label className="text-teal-400 hover:text-teal-300 cursor-pointer underline">
            browse files
            <input
              type="file"
              accept=".pdf,application/pdf"
              className="hidden"
              onChange={handleFileInput}
            />
          </label>
        </p>
        <p className="text-xs text-slate-400 mt-1">Maximum file size: {MAX_SIZE_MB} MB (PDF only)</p>
      </div>

      {selectedFile && (
        <div className="flex items-center justify-between p-3 bg-slate-800/80 border border-slate-700 rounded-lg">
          <div className="flex items-center gap-3">
            <File className="w-5 h-5 text-teal-400" />
            <div>
              <p className="text-sm font-medium text-slate-200">{selectedFile.name}</p>
              <p className="text-xs text-slate-400">{formatBytes(selectedFile.size)}</p>
            </div>
          </div>
          <Button onClick={handleUpload} disabled={uploading}>
            {uploading ? 'Uploading...' : 'Process Document'}
          </Button>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 p-3 bg-rose-950/50 border border-rose-800 text-rose-300 rounded-lg text-sm">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="flex items-center gap-2 p-3 bg-emerald-950/50 border border-emerald-800 text-emerald-300 rounded-lg text-sm">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <span>{success}</span>
        </div>
      )}
    </div>
  );
}

