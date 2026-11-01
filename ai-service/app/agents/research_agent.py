from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IResearchAgent(ABC):
    """
    Interface for future Phase 3 Agentic Research Workflows.
    Responsible for multi-hop reasoning, query decomposition, cross-document
    comparative analysis, and synthesized reporting.
    """

    @abstractmethod
    async def decompose_query(self, complex_query: str) -> List[str]:
        """Decomposes a multi-part user inquiry into atomic sub-questions."""
        pass

    @abstractmethod
    async def synthesize_findings(self, sub_answers: List[Dict[str, Any]]) -> str:
        """Synthesizes intermediate research outputs into a cohesive executive report."""
        pass


class ResearchAgentStub(IResearchAgent):
    """
    Phase 1 Foundation Stub for Research Agent.
    Full agentic capabilities scheduled for delivery in Phase 3.
    """

    async def decompose_query(self, complex_query: str) -> List[str]:
        # Simple baseline for starter scaffold
        return [complex_query]

    async def synthesize_findings(self, sub_answers: List[Dict[str, Any]]) -> str:
        return "Phase 3 Research Agent synthesis placeholder."

