"""
CareConnect AI - Master Multi-Agent Orchestrator
Coordinates sub-agents, enforces safety guardrails, and routes user requests.
"""

from typing import Dict, Any, Optional, List
from .guardrails import GuardrailManager
from .emergency_agent import EmergencyAgent
from .report_decoder import ReportDecoderAgent
from .clinic_finder import ClinicFinderAgent
from .checklist_agent import ChecklistAgent
from .service_locator import ServiceLocatorAgent
from .gemini_client import GeminiClient


class CareConnectOrchestrator:
    """Central orchestrator for the CareConnect AI system."""

    def __init__(self, gemini_api_key: Optional[str] = None):
        self.guardrails = GuardrailManager()
        self.emergency_agent = EmergencyAgent()
        self.report_decoder = ReportDecoderAgent()
        self.clinic_finder = ClinicFinderAgent()
        self.checklist_agent = ChecklistAgent()
        self.service_locator = ServiceLocatorAgent()
        self.gemini_client = GeminiClient(api_key=gemini_api_key)

    def set_api_key(self, api_key: str):
        self.gemini_client.update_api_key(api_key)

    def process_message(
        self,
        message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        country_code: str = "US"
    ) -> Dict[str, Any]:
        """
        Main pipeline:
        1. Emergency Red-Flag detection (Priority 0)
        2. Input guardrails check (Blocks diagnosis/prescription solicitation)
        3. Intent detection & agent dispatch
        4. Output sanitization & disclaimer enforcement
        """
        clean_msg = message.strip()

        # Step 1: Emergency & Red-Flag Check
        emergency_result = self.emergency_agent.check_for_emergency(clean_msg)
        if emergency_result:
            return {
                "type": "emergency",
                "is_emergency": True,
                "content": emergency_result["formatted_message"],
                "data": emergency_result
            }

        # Step 2: Input Guardrail Check (No diagnosis or prescription)
        is_safe, redirect_msg, metadata = self.guardrails.inspect_user_input(clean_msg)
        if not is_safe:
            return {
                "type": "guardrail_blocked",
                "is_emergency": False,
                "content": self.guardrails.sanitize_output(redirect_msg),
                "data": metadata
            }

        # Step 3: Intent Analysis & Dispatch
        msg_lower = clean_msg.lower()

        # Check if user is asking for nearby clinics / hospitals / map
        if any(w in msg_lower for w in ["find clinic", "nearby hospital", "find doctor", "urgent care near", "pharmacy near", "where is the hospital"]):
            clinics = self.clinic_finder.search_nearby()
            resp_text = (
                f"### 📍 Nearby Healthcare Facilities\n\n"
                f"I located **{clinics['total_found']} healthcare centers** near you. "
                f"You can view their operating hours, emergency status, and directions on the interactive map.\n\n"
                f"- **Top match:** **{clinics['facilities'][0]['name']}** ({clinics['facilities'][0]['distance_miles']} miles away)\n"
                f"- **Hours:** {clinics['facilities'][0]['hours']}\n"
                f"- **Phone:** `{clinics['facilities'][0]['phone']}`"
            )
            return {
                "type": "clinic_search",
                "is_emergency": False,
                "content": self.guardrails.sanitize_output(resp_text),
                "data": clinics
            }

        # Check if user is entering lab values or asking about test report
        if any(w in msg_lower for w in ["wbc", "hemoglobin", "cholesterol", "hba1c", "glucose", "tsh", "alt", "creatinine", "lab report", "blood test"]):
            report_result = self.report_decoder.parse_report_text(clean_msg)
            return {
                "type": "lab_report",
                "is_emergency": False,
                "content": self.guardrails.sanitize_output(report_result["summary"]),
                "data": report_result
            }

        # Check if user wants appointment preparation checklist
        if any(w in msg_lower for w in ["appointment", "prepare for doctor", "checklist", "questions to ask doctor", "visit prep"]):
            checklist = self.checklist_agent.generate_checklist(
                chief_complaint=clean_msg,
                duration="Recent weeks"
            )
            return {
                "type": "appointment_checklist",
                "is_emergency": False,
                "content": self.guardrails.sanitize_output(checklist["formatted_markdown"]),
                "data": checklist
            }

        # Check for service triage / where should I go
        if any(w in msg_lower for w in ["where should i go", "er or urgent care", "which doctor", "need specialist", "should i see"]):
            triage_res = self.service_locator.triage_symptom(clean_msg)
            msg = (
                f"### 🧭 Healthcare Service Guidance\n\n"
                f"**Recommendation:** **{triage_res['recommendation']}**\n\n"
                f"**Why:** {triage_res['reasoning']}\n\n"
                f"**When to choose this level:** {triage_res['level_info'].get('when_to_go', '')}"
            )
            return {
                "type": "service_triage",
                "is_emergency": False,
                "content": self.guardrails.sanitize_output(msg),
                "data": triage_res
            }

        # Step 4: Conversational Fallback (Gemini or Built-in Health Assistant)
        if self.gemini_client.is_configured():
            gemini_resp = self.gemini_client.generate_chat_response(
                user_message=clean_msg,
                conversation_history=conversation_history
            )
            if gemini_resp:
                return {
                    "type": "conversational_gemini",
                    "is_emergency": False,
                    "content": self.guardrails.sanitize_output(gemini_resp),
                    "data": {"engine": "gemini"}
                }

        # Built-in offline conversational response
        default_reply = (
            f"Hello! I am **CareConnect AI**, your personal healthcare assistance companion.\n\n"
            f"Here are the ways I can support you:\n"
            f"1. **Decode Medical Reports:** Paste lab test lines (like *WBC*, *Hemoglobin*, *Lipid Panel*, *HbA1c*) to understand them in plain English.\n"
            f"2. **Find Nearby Care:** Discover local emergency rooms, walk-in urgent care clinics, and pharmacies with interactive maps.\n"
            f"3. **Doctor Visit Checklist:** Create a tailored list of questions and symptom summaries for your next appointment.\n"
            f"4. **Care Triage:** Find out whether an ER, urgent care, or primary care doctor is best suited for your situation.\n"
            f"5. **Emergency Support:** Instant access to emergency numbers and dispatcher guidance.\n\n"
            f"*Please note: I cannot diagnose conditions or prescribe medications.* How may I assist you today?"
        )

        return {
            "type": "conversational_offline",
            "is_emergency": False,
            "content": self.guardrails.sanitize_output(default_reply),
            "data": {"engine": "offline_rule_system"}
        }
