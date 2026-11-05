"""
CareConnect AI - Google Gemini API Client
Integrates Google Gemini (via google-genai SDK) with strict medical guardrails.
Gracefully falls back to offline rule-engine when no API key is configured.
"""

import os
from typing import Optional, Dict, Any, List

SYSTEM_PROMPT = """
You are CareConnect AI, an intelligent, empathetic, and strictly compliant healthcare assistance companion.
Your primary role is to help patients understand healthcare information, navigate the medical system, and prepare for doctor visits.

CRITICAL MEDICAL DIRECTIVES & GUARDRAILS:
1. NEVER diagnose an illness, condition, or disease. Do NOT say "You have X".
2. NEVER prescribe, recommend medications, or specify dosages. Do NOT suggest taking any specific pharmaceutical product.
3. If the user mentions red-flag emergencies (chest pain, stroke signs, difficulty breathing, suicide/self-harm), immediately instruct them to seek emergency services (911/112/988).
4. For lab reports:
   - Explain what each test measures in simple terms using everyday analogies.
   - Explain what reference ranges represent (95% statistical normal of healthy individuals).
   - Discuss non-disease factors (hydration, recent meal, stress, vigorous exercise).
   - Provide thoughtful questions for the patient to ask their doctor.
5. Maintain a warm, clear, accessible, and supportive tone.
6. Always end with the reminder that you provide health navigation and educational information only, not medical diagnosis or treatment.
"""

class GeminiClient:
    """Wrapper around google-genai SDK with safety instructions and fallback."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = None
        self._init_client()

    def _init_client(self):
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                self.client = None

    def update_api_key(self, api_key: str):
        """Updates the active API key and re-initializes client."""
        self.api_key = api_key.strip()
        self._init_client()

    def is_configured(self) -> bool:
        return self.client is not None

    def generate_chat_response(
        self,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        model_name: str = "gemini-2.5-flash"
    ) -> Optional[str]:
        """
        Sends conversation to Gemini API with strict system instructions.
        Returns generated text or None if client is not configured or fails.
        """
        if not self.client:
            return None

        try:
            from google.genai import types

            contents = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg.get("role") == "user" else "model"
                    contents.append(types.Content(
                        role=role,
                        parts=[types.Part.from_text(text=msg.get("content", ""))]
                    ))

            contents.append(types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_message)]
            ))

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.3,
            )

            response = self.client.models.generate_content(
                model=model_name,
                contents=contents,
                config=config
            )
            return response.text
        except Exception:
            return None

    def analyze_lab_report_vision(
        self,
        image_bytes: bytes,
        mime_type: str = "image/jpeg",
        model_name: str = "gemini-2.5-flash"
    ) -> Optional[str]:
        """
        Analyzes an uploaded photo or PDF of a lab report using Gemini Vision.
        """
        if not self.client:
            return None

        try:
            from google.genai import types

            prompt = (
                "Please read this medical lab report and explain it in simple, patient-friendly terms:\n"
                "1. List all detected tests, their observed values, and standard reference ranges.\n"
                "2. Clearly explain what each test measures using everyday analogies.\n"
                "3. Mention lifestyle or non-disease factors (hydration, stress, recent meals) that might influence results.\n"
                "4. Suggest 3-5 clear questions the patient can ask their physician.\n"
                "Remember: DO NOT diagnose conditions or prescribe medications."
            )

            parts = [
                types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                types.Part.from_text(text=prompt)
            ]

            config = types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.2,
            )

            response = self.client.models.generate_content(
                model=model_name,
                contents=parts,
                config=config
            )
            return response.text
        except Exception:
            return None
