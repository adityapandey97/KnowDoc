import React from 'react';
import { Card } from '../../components/ui/Card.jsx';
import { DocumentUploader } from '../../components/documents/DocumentUploader.jsx';
import { DocumentList } from '../../components/documents/DocumentList.jsx';
import { RefreshCw, FileText } from 'lucide-react';
import { Button } from '../../components/ui/Button.jsx';

export function DocumentsModule({ documents, onRefresh, onDelete, onSelect, selectedId }) {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
            <FileText className="w-6 h-6 text-teal-400" />
            Document Management
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Upload PDF files to parse, chunk, embed, and index into PostgreSQL pgvector.
          </p>
        </div>
        <Button variant="outline" size="sm" onClick={onRefresh}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" />
          Refresh
        </Button>
      </div>

      <Card>
        <h3 className="text-sm font-semibold text-slate-200 mb-3">Upload New Document</h3>
        <DocumentUploader onUploadSuccess={onRefresh} />
      </Card>

      <div>
        <h3 className="text-sm font-semibold text-slate-200 mb-3">
          Indexed Documents ({documents.length})
        </h3>
        <DocumentList
          documents={documents}
          onDelete={onDelete}
          onSelect={onSelect}
          selectedId={selectedId}
        />
      </div>
    </div>
  );
}

