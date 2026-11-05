"""
CareConnect AI - Appointment Preparation Checklist Agent
Generates tailored, highly organized visit briefs and doctor question checklists.
"""

from typing import Dict, Any, List

DEFAULT_WHAT_TO_BRING = [
    "Government Photo ID & Health Insurance / Medicare card",
    "List of all current medications, vitamins, and over-the-counter supplements (with dosages)",
    "Copies of recent lab results, imaging discs, or hospital discharge summaries",
    "List of known allergies (medications, foods, latex)",
    "Payment method for clinic copay or deductible",
    "Pen and notepad or phone for noting doctor recommendations",
    "Name and contact information of your preferred pharmacy"
]

CATEGORY_QUESTIONS = {
    "general": [
        "What do you think is causing my main symptom?",
        "Are there any diagnostic tests or labs we should order today?",
        "What lifestyle or dietary changes would make the biggest difference?",
        "What symptoms or red flags should prompt me to call you or seek urgent care?",
        "When should I schedule a follow-up appointment?"
    ],
    "pain": [
        "What is the most likely source or mechanism of this pain?",
        "Are non-medication therapies (physical therapy, heat/ice, stretches) recommended?",
        "What activities or movements should I temporarily avoid to prevent worsening?",
        "How long do patients typically take to notice improvement?",
        "If the pain does not subside within 2 weeks, what is our next step?"
    ],
    "fatigue": [
        "Could my tiredness be linked to vitamin deficiencies, thyroid, or iron levels?",
        "Would a sleep study or evaluation for sleep apnea be beneficial?",
        "Could any of my current daily medications be contributing to fatigue?",
        "What daily energy-pacing strategies do you recommend?"
    ],
    "blood_pressure": [
        "What is my blood pressure reading today, and what is our target range?",
        "How often should I log my blood pressure readings at home?",
        "What dietary approaches (e.g. sodium reduction) do you recommend starting with?",
        "Are there specific times of day I should take my readings?"
    ],
    "cholesterol": [
        "Looking at my full lipid panel, what is my overall 10-year cardiovascular risk?",
        "What specific changes in dietary fats and exercise produce the best results?",
        "How many months should I practice these lifestyle changes before re-testing?",
        "At what threshold would you recommend discussing cholesterol medication?"
    ]
}


class ChecklistAgent:
    """Creates doctor visit preparation checklists and consultation briefs."""

    def generate_checklist(
        self,
        chief_complaint: str,
        duration: str = "",
        severity: int = 5,
        medications: List[str] = None,
        allergies: List[str] = None,
        custom_concerns: str = ""
    ) -> Dict[str, Any]:
        """
        Builds a comprehensive consultation checklist.
        """
        meds = medications or []
        allergy_list = allergies or ["No known drug allergies reported"]

        # Select relevant questions
        complaint_lower = chief_complaint.lower()
        selected_questions = []

        if any(w in complaint_lower for w in ["pain", "hurt", "ache", "stiffness", "sore"]):
            selected_questions.extend(CATEGORY_QUESTIONS["pain"][:3])
        elif any(w in complaint_lower for w in ["tired", "fatigue", "exhaust", "sleep"]):
            selected_questions.extend(CATEGORY_QUESTIONS["fatigue"][:3])
        elif any(w in complaint_lower for w in ["pressure", "hypertension", "bp"]):
            selected_questions.extend(CATEGORY_QUESTIONS["blood_pressure"][:3])
        elif any(w in complaint_lower for w in ["cholesterol", "lipid", "triglyceride"]):
            selected_questions.extend(CATEGORY_QUESTIONS["cholesterol"][:3])

        # Fill with general questions
        for q in CATEGORY_QUESTIONS["general"]:
            if len(selected_questions) >= 5:
                break
            if q not in selected_questions:
                selected_questions.append(q)

        # Build printable markdown brief
        brief_lines = [
            "# 📋 Patient Consultation Brief",
            "*(Bring this summary with you or show it to your nurse/physician)*",
            "",
            "### 1. Primary Reason for Visit",
            f"- **Chief Concern:** {chief_complaint or 'Routine checkup / Consultation'}",
            f"- **Duration:** {duration or 'Not specified'}",
            f"- **Discomfort Level (1-10):** {severity}/10",
            "",
            "### 2. Current Medications & Supplements",
        ]

        if meds:
            for m in meds:
                brief_lines.append(f"- [ ] {m}")
        else:
            brief_lines.append("- *No daily medications reported*")

        brief_lines.extend([
            "",
            "### 3. Allergies & Sensitivities",
        ])
        for a in allergy_list:
            brief_lines.append(f"- ⚠️ {a}")

        if custom_concerns:
            brief_lines.extend([
                "",
                "### 4. Patient's Specific Questions & Notes",
                f"> {custom_concerns}"
            ])

        brief_lines.extend([
            "",
            "### 5. Questions to Ask During Your Visit",
        ])
        for idx, q in enumerate(selected_questions, 1):
            brief_lines.append(f"{idx}. [ ] {q}")

        brief_lines.extend([
            "",
            "### 6. What to Bring to Your Appointment",
        ])
        for item in DEFAULT_WHAT_TO_BRING:
            brief_lines.append(f"- [ ] {item}")

        brief_lines.extend([
            "",
            "---",
            "*Prepared with CareConnect AI • Please record your doctor's recommendations in the notes section.*"
        ])

        return {
            "chief_complaint": chief_complaint,
            "duration": duration,
            "severity": severity,
            "medications": meds,
            "allergies": allergy_list,
            "what_to_bring": DEFAULT_WHAT_TO_BRING,
            "questions_to_ask": selected_questions,
            "formatted_markdown": "\n".join(brief_lines)
        }
