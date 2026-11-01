import React from 'react';
import { Card } from '../../components/ui/Card.jsx';
import { Compass, Network, Sparkles, CheckSquare } from 'lucide-react';

export function ResearchModule() {
  const roadmapItems = [
    {
      title: 'Autonomous Query Decomposition',
      desc: 'Deconstruct complex multi-faceted research queries into granular sub-questions executed across distinct document partitions.',
      status: 'Phase 3'
    },
    {
      title: 'Cross-Document Comparison Matrix',
      desc: 'Automatically extract competing claims, numerical differences, or terms across dozens of documents into a synthesized tabular view.',
      status: 'Phase 3'
    },
    {
      title: 'Hybrid Enterprise & Real-Time Web Grounding',
      desc: 'Merge proprietary internal document citations with live external web sources for comprehensive market and competitive intelligence.',
      status: 'Phase 3'
    }
  ];

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div>
        <h2 className="text-xl font-bold text-slate-100 flex items-center gap-2">
          <Compass className="w-6 h-6 text-teal-400" />
          Autonomous Deep Research Workflows
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          Architectural foundation for multi-agent synthesis and cross-document reasoning.
        </p>
      </div>

      <Card className="bg-gradient-to-br from-slate-800 to-slate-900 border-teal-500/20">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-2 rounded-lg bg-teal-500/10 text-teal-400 border border-teal-500/30">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-sm font-semibold text-slate-100">Multi-Hop Research Pipeline</h3>
            <p className="text-xs text-slate-400">Scheduled for active rollout in Phase 3</p>
          </div>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          While Phase 1 provides the core pgvector indexing and conversational RAG foundation, the AI service includes starter scaffolding for <code className="text-teal-300">IResearchAgent</code> and <code className="text-teal-300">MultiDocWorkflow</code>.
        </p>
      </Card>

      <div className="space-y-3">
        {roadmapItems.map((item, idx) => (
          <Card key={idx} className="flex items-start gap-4 p-4">
            <div className="p-2 rounded-lg bg-slate-900 border border-slate-700 text-teal-400 flex-shrink-0">
              <Network className="w-5 h-5" />
            </div>
            <div className="flex-1">
              <div className="flex items-center justify-between mb-1">
                <h4 className="text-sm font-semibold text-slate-200">{item.title}</h4>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded bg-teal-950 border border-teal-800 text-teal-400">
                  {item.status}
                </span>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

