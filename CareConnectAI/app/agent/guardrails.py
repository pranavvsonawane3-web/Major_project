"""
CareConnect AI - Medical Safety & Ethics Guardrails
Ensures that the AI NEVER diagnoses diseases or prescribes medications.
Enforces clinical boundary protections and standard medical disclaimers.
"""

import re
from typing import Tuple, Dict, Any, List

STANDARD_DISCLAIMER = (
    "Disclaimer: CareConnect AI provides health navigation and educational information only. "
    "It does not provide medical diagnosis, treatment plans, or prescription recommendations. "
    "Always consult a licensed medical provider or call emergency services for acute medical concerns."
)

# Patterns that indicate a user is asking for a diagnosis or medication prescription
DIAGNOSIS_INTENT_PATTERNS = [
    r"\b(diagnose\s+me|give\s+me\s+a\s+diagnosis|do\s+i\s+have|what\s+disease\s+do\s+i\s+have)\b",
    r"\b(what\s+illness\s+is\s+this|could\s+this\s+be\s+cancer|am\s+i\s+diabetic)\b",
    r"\b(tell\s+me\s+my\s+diagnosis|is\s+this\s+a\s+tumor)\b"
]

PRESCRIPTION_INTENT_PATTERNS = [
    r"\b(prescribe\s+(me|a|some)|what\s+antibiotic\s+should\s+i\s+take|what\s+pill\s+should\s+i\s+take)\b",
    r"\b(what\s+dose|what\s+dosage\s+of|how\s+many\s+mg\s+of\s+\w+\s+should\s+i\s+take)\b",
    r"\b(write\s+me\s+a\s+prescription|can\s+you\s+prescribe)\b"
]

# Patterns in generated output that must be sanitized if an LLM or module slips up
UNSAFE_OUTPUT_PATTERNS = [
    (r"\b(you\s+have\s+(diabetes|cancer|hypertension|anemia|infection|covid|pneumonia|depression))\b",
     r"these findings may be associated with \2, which your doctor can evaluate"),
    (r"\b(i\s+diagnose\s+you\s+with)\b", r"your healthcare provider may investigate"),
    (r"\b(take\s+\d+\s*(mg|milligrams|tablets|pills)\s+of)\b", r"discuss with your doctor or pharmacist about"),
    (r"\b(i\s+prescribe|you\s+should\s+take\s+(amoxicillin|ibuprofen|antibiotics|adderall|xanax|metformin))\b",
     r"options your doctor might discuss with you include \2")
]


class GuardrailManager:
    """Manages input and output safety checks for medical compliance."""

    @staticmethod
    def inspect_user_input(text: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Inspects incoming user input for attempts to solicit a diagnosis or prescription.
        Returns: (is_safe, redirect_message, metadata)
        """
        text_lower = text.lower().strip()

        # Check for direct prescription solicitations
        for pattern in PRESCRIPTION_INTENT_PATTERNS:
            if re.search(pattern, text_lower):
                message = (
                    "**Clinical Safety Boundary:** I cannot prescribe medications, recommend specific drugs, "
                    "or suggest medication dosages. Medication decisions must always be made by a licensed healthcare "
                    "provider who knows your medical history, allergies, and current prescriptions.\n\n"
                    "**How I can help instead:**\n"
                    "- Help you locate a nearby urgent care clinic or primary care doctor.\n"
                    "- Create a checklist of questions to ask your doctor or pharmacist about treatment options.\n"
                    "- Explain the general purpose of standard medical terms or lab results."
                )
                return False, message, {"violation_type": "prescription_request", "action": "blocked"}

        # Check for direct diagnosis solicitations
        for pattern in DIAGNOSIS_INTENT_PATTERNS:
            if re.search(pattern, text_lower):
                message = (
                    "**Clinical Safety Boundary:** I cannot provide medical diagnoses or tell you whether you "
                    "have a specific disease. An accurate diagnosis requires physical examinations, clinical history, "
                    "and professional medical interpretation.\n\n"
                    "**How I can help instead:**\n"
                    "- Help you identify the right type of specialist (e.g. Dermatologist, Cardiologist, ENT) for your symptoms.\n"
                    "- Prepare a structured symptom timeline and question checklist for your doctor's visit.\n"
                    "- Translate complex lab test results into plain, easy-to-understand language."
                )
                return False, message, {"violation_type": "diagnosis_request", "action": "reframed"}

        return True, "", {"violation_type": "none", "action": "pass"}

    @staticmethod
    def sanitize_output(text: str) -> str:
        """
        Sweeps agent output to guarantee no declarative diagnosis or prescription is made.
        Appends the medical disclaimer if not already present.
        """
        sanitized = text
        for pattern, replacement in UNSAFE_OUTPUT_PATTERNS:
            sanitized = re.sub(pattern, replacement, sanitized, flags=re.IGNORECASE)

        # Ensure disclaimer is included
        if "CareConnect AI provides health navigation and educational information only" not in sanitized:
            sanitized = f"{sanitized}\n\n---\n*{STANDARD_DISCLAIMER}*"

        return sanitized

    @staticmethod
    def get_standard_disclaimer() -> str:
        return STANDARD_DISCLAIMER
