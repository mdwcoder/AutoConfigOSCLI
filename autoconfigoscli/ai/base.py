from abc import ABC, abstractmethod
from typing import Dict, Any, List

class AIProvider(ABC):
    @abstractmethod
    def recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ask AI to recommend a profile based on context.
        Should return JSON with: recommended_profile, alternatives, reasoning, risks.
        """
        pass

    @abstractmethod
    def explain(self, context: Dict[str, Any], query: str) -> str:
        """
        Ask AI to explain something specific or generic logic.
        """
        pass
