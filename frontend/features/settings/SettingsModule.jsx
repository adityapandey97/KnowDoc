import React, { useEffect, useState } from 'react';
import { Card } from '../../components/ui/Card.jsx';
import { Settings, Server, Database, Shield, Cpu } from 'lucide-react';
import { Badge } from '../../components/ui/Badge.jsx';

export function SettingsModule() {
  const [health, setHealth] = useState(null);

  useEffect(() => {
    fetch('/api/v1/health')
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch(() => setHealth({ status: 'offline' }));
  }, []);

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Settings className="w-6 h-6 text-teal-400" />
          System Architecture & Settings
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Review environment parameters, datastore health, and vector indexing configurations.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <div className="flex items-center gap-3 mb-3">
            <Server className="w-5 h-5 text-teal-400" />
            <h3 className="text-sm font-semibold text-slate-200">Express API Gateway</h3>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Status</span>
              <Badge status={health?.status === 'healthy' ? 'ready' : 'failed'} label={health?.status || 'checking'} />
            </div>
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Runtime</span>
              <span className="text-slate-200">Node.js 22 LTS (ES Modules)</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Port</span>
              <span className="text-slate-200">5000</span>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3 mb-3">
            <Cpu className="w-5 h-5 text-teal-400" />
            <h3 className="text-sm font-semibold text-slate-200">FastAPI AI Service</h3>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Runtime</span>
              <span className="text-slate-200">Python 3.12+</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Vector Dimensions</span>
              <span className="text-slate-200 font-mono">1536 (HNSW)</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Authentication</span>
              <span className="text-slate-200">Internal Key (X-Internal-Service-Key)</span>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3 mb-3">
            <Database className="w-5 h-5 text-teal-400" />
            <h3 className="text-sm font-semibold text-slate-200">Storage & Vector DB</h3>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Application State</span>
              <span className="text-slate-200">MongoDB 7.0</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Vector Index</span>
              <span className="text-slate-200">PostgreSQL 16 + pgvector</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Queue Broker</span>
              <span className="text-slate-200">Redis 7 + BullMQ</span>
            </div>
          </div>
        </Card>

        <Card>
          <div className="flex items-center gap-3 mb-3">
            <Shield className="w-5 h-5 text-teal-400" />
            <h3 className="text-sm font-semibold text-slate-200">Security & Isolation</h3>
          </div>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Multi-Tenancy</span>
              <span className="text-slate-200">User-partitioned vector queries</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-700/50">
              <span className="text-slate-400">Upload Defense</span>
              <span className="text-slate-200">Binary magic byte (%PDF) check</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Prompt Isolation</span>
              <span className="text-slate-200">XML-delimited untrusted context</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}

