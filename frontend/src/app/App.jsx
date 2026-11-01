import React, { useState, useEffect } from 'react';
import { Navbar } from '../../components/layout/Navbar.jsx';
import { Sidebar } from '../../components/layout/Sidebar.jsx';
import { DocumentsModule } from '../../features/documents/DocumentsModule.jsx';
import { ChatModule } from '../../features/chat/ChatModule.jsx';
import { ResearchModule } from '../../features/research/ResearchModule.jsx';
import { SettingsModule } from '../../features/settings/SettingsModule.jsx';
import { AuthModule } from '../../features/auth/AuthModule.jsx';
import { documentService } from '../../services/documentService.js';
import { chatService } from '../../services/chatService.js';

export function App() {
  const [activeTab, setActiveTab] = useState('documents');
  const [user, setUser] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [selectedDoc, setSelectedDoc] = useState(null);

  const fetchDocuments = async () => {
    try {
      const res = await documentService.listDocuments();
      if (res.data) setDocuments(res.data);
    } catch {
      // In dev with mock or offline DB, keep fallback sample data
      setDocuments([
        {
          id: 'doc_sample_1',
          filename: 'Q3-Financial-Analysis.pdf',
          status: 'ready',
          sizeBytes: 1024 * 1024 * 2.4,
          pageCount: 32,
          chunkCount: 94,
          createdAt: new Date().toISOString()
        }
      ]);
    }
  };

  const fetchConversations = async () => {
    try {
      const res = await chatService.listConversations();
      if (res.data) setConversations(res.data);
    } catch {
      setConversations([
        { id: 'convo_1', title: 'Q3 Financial Analysis Discussion' }
      ]);
    }
  };

  useEffect(() => {
    fetchDocuments();
    fetchConversations();
  }, []);

  const handleDeleteDocument = async (id) => {
    try {
      await documentService.deleteDocument(id);
      fetchDocuments();
    } catch {
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-900 text-slate-100">
      <Navbar activeTab={activeTab} setActiveTab={setActiveTab} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar
          documents={documents}
          conversations={conversations}
          onNewChat={() => setActiveTab('chat')}
          activeDocId={selectedDoc?.id}
        />

        <main className="flex-1 overflow-y-auto p-6 md:p-8">
          <div className="max-w-7xl mx-auto">
            {activeTab === 'documents' && (
              <DocumentsModule
                documents={documents}
                onRefresh={fetchDocuments}
                onDelete={handleDeleteDocument}
                onSelect={(doc) => {
                  setSelectedDoc(doc);
                  setActiveTab('chat');
                }}
                selectedId={selectedDoc?.id}
              />
            )}

            {activeTab === 'chat' && (
              <ChatModule
                documents={documents}
                selectedDoc={selectedDoc}
                onSelectDoc={setSelectedDoc}
              />
            )}

            {activeTab === 'research' && <ResearchModule />}

            {activeTab === 'settings' && <SettingsModule />}

            {activeTab === 'auth' && (
              <AuthModule
                onAuthSuccess={(u) => {
                  setUser(u);
                  setActiveTab('documents');
                }}
              />
            )}
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;

