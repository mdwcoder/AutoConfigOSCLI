import os
import json
import logging
from typing import Dict, Any, Optional
from .base import AIProvider

# Try importing google.generativeai if installed
try:
    import google.generativeai as genai
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False

class GeminiProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if HAS_GEMINI and self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None

    @property
    def is_available(self) -> bool:
        return HAS_GEMINI and self.model is not None

    def recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_available:
            return {"error": "Gemini not available"}

        prompt = f"""
        You are a system configuration expert. Analyze the following user context and available profiles to recommend the best fit.
        
        Context:
        {json.dumps(context, indent=2)}

        Task:
        1. Select the BEST single profile from the available list (in context['profiles']).
        2. Identify 1-2 alternatives.
        3. Explain reasoning carefully (hardware, role, etc.).
        4. List any potential risks.

        Output strictly JSON:
        {{
            "recommended_profile": "name",
            "alternatives": ["name1", "name2"],
            "reasoning": "...",
            "risks": ["..."]
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Cleanup markdown code blocks if present
            text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(text)
        except Exception as e:
            logging.error(f"Gemini error: {e}")
            return {"error": str(e)}

    def explain(self, context: Dict[str, Any], query: str) -> str:
        if not self.is_available:
            return "Gemini provider is not configured or available."

        prompt = f"""
        Context:
        {json.dumps(context, indent=2)}

        User Question: {query}
        
        Provide a concise, technical explanation.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error generation explanation: {e}"
