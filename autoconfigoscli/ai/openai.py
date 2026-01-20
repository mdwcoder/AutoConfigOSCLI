import os
import json
import logging
from typing import Dict, Any
from .base import AIProvider

# Try importing openai if installed
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

class OpenAIProvider(AIProvider):
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if HAS_OPENAI and self.api_key:
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            self.client = None

    @property
    def is_available(self) -> bool:
        return HAS_OPENAI and self.client is not None

    def recommend(self, context: Dict[str, Any]) -> Dict[str, Any]:
        if not self.is_available:
            return {"error": "OpenAI not available"}

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
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful CLI configuration assistant."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            text = response.choices[0].message.content
            return json.loads(text)
        except Exception as e:
            logging.error(f"OpenAI error: {e}")
            return {"error": str(e)}

    def explain(self, context: Dict[str, Any], query: str) -> str:
        if not self.is_available:
            return "OpenAI provider is not configured or available."

        prompt = f"""
        Context:
        {json.dumps(context, indent=2)}

        User Question: {query}
        
        Provide a concise, technical explanation.
        """
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful CLI configuration assistant."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generation explanation: {e}"
