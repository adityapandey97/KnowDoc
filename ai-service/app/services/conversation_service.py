from typing import List, Dict, Any
from app.schemas.chat import ChatMessage
from app.core.logging import logger

class ConversationService:
    """
    Manages bounded conversational memory for multi-turn question-answering.
    Ensures dialogue history is clearly separated from verified document evidence.
    """

    def __init__(self, max_history_turns: int = 6):
        self.max_history_turns = max_history_turns

    def prepare_bounded_history(
        self,
        history: List[ChatMessage],
        current_query: str
    ) -> List[Dict[str, str]]:
        """
        Extracts the most recent turns up to max_history_turns.
        Strips unnecessary noise and formats as standard message dictionaries.
        """
        if not history:
            return []

        # Keep last N messages
        recent = history[-self.max_history_turns :]
        formatted: List[Dict[str, str]] = []

        for msg in recent:
            role = msg.role.lower()
            if role not in ("user", "assistant"):
                continue

            content = msg.content.strip()
            # Truncate overly long past turns to protect context window
            if len(content) > 1000:
                content = content[:1000] + "..."

            formatted.append({"role": role, "content": content})

        logger.debug(f"Prepared {len(formatted)} bounded history messages for follow-up query")
        return formatted

conversation_service = ConversationService()

