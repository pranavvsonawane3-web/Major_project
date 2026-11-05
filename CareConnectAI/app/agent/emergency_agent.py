"""
CareConnect AI - Emergency Agent
Detects life-threatening symptoms, red-flags, and provides instant crisis guidance.
"""

import json
import os
import re
from typing import Dict, Any, Optional

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "emergency_numbers.json")

class EmergencyAgent:
    """Detects emergency situations and returns critical action guidance."""

    def __init__(self):
        self.emergency_data = self._load_data()
        self.red_flags = self.emergency_data.get("red_flag_symptoms", [])
        self.countries = self.emergency_data.get("countries", {})
        self.dispatcher_instructions = self.emergency_data.get("dispatcher_instructions", [])

    def _load_data(self) -> Dict[str, Any]:
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def check_for_emergency(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Scans query for critical red-flag terms.
        Returns emergency guidance payload if a red flag is found, else None.
        """
        query_lower = query.lower()
        matched_flags = []

        for flag in self.red_flags:
            # Match whole phrase or word boundary
            pattern = r"\b" + re.escape(flag) + r"\b"
            if re.search(pattern, query_lower):
                matched_flags.append(flag)

        # Check for suicide / self-harm explicit patterns
        crisis_patterns = [
            r"\b(suicide|kill\s+myself|end\s+my\s+life|don't\s+want\s+to\s+live|overdose)\b"
        ]
        for p in crisis_patterns:
            if re.search(p, query_lower):
                if "crisis / self-harm" not in matched_flags:
                    matched_flags.append("mental health crisis")

        if matched_flags:
            return self.build_emergency_response(matched_flags, query)

        return None

    def build_emergency_response(self, matched_flags: list, original_query: str, country_code: str = "US") -> Dict[str, Any]:
        """Constructs an urgent emergency card and protocol."""
        country_info = self.countries.get(country_code.upper(), self.countries.get("US", {}))
        is_mental_health = any("crisis" in f or "suicide" in f or "life" in f for f in matched_flags)

        headline = "🚨 POTENTIAL MEDICAL EMERGENCY DETECTED"
        if is_mental_health:
            headline = "💛 IMMEDIATE CRISIS SUPPORT AVAILABLE"

        main_number = country_info.get("mental_health_crisis" if is_mental_health else "general", "911")

        message = (
            f"### {headline}\n\n"
            f"Your request mentioned potential emergency indicators: **{', '.join(matched_flags)}**.\n\n"
            f"**Please do not wait for online advice. Immediate medical attention may be required.**\n\n"
            f"📞 **Call Emergency Services immediately:** **{main_number}** ({country_info.get('name', 'Local')})\n\n"
        )

        if is_mental_health:
            message += (
                f"- **Suicide & Crisis Lifeline:** Call or text **{country_info.get('mental_health_crisis', '988')}**\n"
                f"- **Crisis Text Line:** {country_info.get('crisis_text', 'Text HOME to 741741')}\n"
                f"- **Free, confidential, 24/7 support.** You are not alone.\n\n"
            )
        else:
            message += (
                f"- **Local Emergency Number:** `{country_info.get('general', '911')}`\n"
                f"- **Poison Control Center:** `{country_info.get('poison_control', '1-800-222-1222')}`\n\n"
                f"#### 🎙️ What to tell the 911/112 operator:\n"
            )
            for step in self.dispatcher_instructions:
                message += f"1. {step}\n"

        message += "\n*If you are with the patient, stay on the phone with the dispatcher and follow their spoken guidance.*"

        return {
            "is_emergency": True,
            "matched_red_flags": matched_flags,
            "emergency_number": main_number,
            "country": country_info.get("name", "United States"),
            "formatted_message": message,
            "dispatcher_instructions": self.dispatcher_instructions,
            "country_hotlines": country_info
        }

    def get_all_country_hotlines(self) -> Dict[str, Any]:
        """Returns hotlines for all configured regions."""
        return self.countries
