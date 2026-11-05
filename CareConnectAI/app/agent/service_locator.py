"""
CareConnect AI - Service Locator & Healthcare Triage Agent
Helps users identify the appropriate tier of healthcare service (ER, Urgent Care, Primary Care, Specialist).
"""

import json
import os
import re
from typing import Dict, Any, List

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "specialties_map.json")


class ServiceLocatorAgent:
    """Guides users to the appropriate care setting based on symptoms."""

    def __init__(self):
        self.data = self._load_data()
        self.care_levels = self.data.get("care_levels", {})
        self.specialties = self.data.get("specialties", {})
        self.triage_scenarios = self.data.get("triage_scenarios", [])

    def _load_data(self) -> Dict[str, Any]:
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def triage_symptom(self, symptom_text: str) -> Dict[str, Any]:
        """
        Recommends appropriate level of healthcare service.
        """
        text_lower = symptom_text.lower()

        # Check for emergency level
        emergency_words = [
            "chest pain", "crushing", "stroke", "paralysis", "can't breathe", "cannot breathe",
            "severe breathing", "unconscious", "head injury passing out", "severe bleeding"
        ]
        if any(w in text_lower for w in emergency_words):
            return {
                "care_level": "emergency",
                "level_info": self.care_levels.get("emergency", {}),
                "matched_specialty": None,
                "recommendation": "🚨 Immediate Emergency Department (ER) or Call 911 / 112.",
                "reasoning": "These symptoms require urgent in-hospital diagnostic testing, resuscitation equipment, or rapid stabilization."
            }

        # Check for urgent care indicators
        urgent_words = [
            "sprain", "twisted", "cut needing stitches", "mild burn", "suspected fracture",
            "ear pain", "painful urination", "pink eye", "asthma flare mild", "urgent care"
        ]
        if any(w in text_lower for w in urgent_words):
            return {
                "care_level": "urgent_care",
                "level_info": self.care_levels.get("urgent_care", {}),
                "matched_specialty": None,
                "recommendation": "⚡ Urgent Care Center (Walk-in)",
                "reasoning": "Urgent Care clinics provide same-day walk-in evaluations, simple X-rays, stitches, and basic lab tests without the long wait or expense of an ER."
            }

        # Check for matching specialty
        for spec_name, spec_info in self.specialties.items():
            triggers = spec_info.get("common_triggers", [])
            for trig in triggers:
                if re.search(r"\b" + re.escape(trig) + r"\b", text_lower):
                    return {
                        "care_level": "specialist",
                        "level_info": self.care_levels.get("specialist", {}),
                        "matched_specialty": spec_name,
                        "specialty_description": spec_info.get("description", ""),
                        "recommendation": f"🔬 Specialist Consultation: {spec_name}",
                        "reasoning": f"Your mention of '{trig}' aligns with {spec_name}. You may ask your primary care physician for a referral or book with an in-network specialist."
                    }

        # Default to Primary Care
        return {
            "care_level": "primary_care",
            "level_info": self.care_levels.get("primary_care", {}),
            "matched_specialty": None,
            "recommendation": "🩺 Primary Care Physician (PCP) / Family Doctor / Telehealth",
            "reasoning": "Your primary care doctor is the ideal starting point to evaluate your overall health, order initial blood tests or imaging, and refer you to a specialist if necessary."
        }

    def get_all_specialties(self) -> Dict[str, Any]:
        return self.specialties

    def get_care_levels(self) -> Dict[str, Any]:
        return self.care_levels
