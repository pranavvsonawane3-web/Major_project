"""
CareConnect AI - Medical Report Simplifier Agent
Translates complex medical lab reports into simple, accessible language.
Strictly non-diagnostic: provides analogies, explanations, and questions for doctors.
"""

import json
import os
import re
from typing import Dict, Any, List, Optional

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "lab_tests_knowledge.json")

# Regex pattern matchers for common lab tests
TEST_PATTERNS = {
    "wbc": [r"\b(wbc|white\s+blood\s+cell[s]?)\b[^\d]*(\d+\.?\d*)", r"\bleukocyte[s]?\b[^\d]*(\d+\.?\d*)"],
    "rbc": [r"\b(rbc|red\s+blood\s+cell[s]?)\b[^\d]*(\d+\.?\d*)", r"\berythrocyte[s]?\b[^\d]*(\d+\.?\d*)"],
    "hemoglobin": [r"\b(hemoglobin|hgb|hb)\b[^\d]*(\d+\.?\d*)"],
    "hematocrit": [r"\b(hematocrit|hct)\b[^\d]*(\d+\.?\d*)"],
    "platelets": [r"\b(platelet[s]?|plt)\b[^\d]*(\d+\.?\d*)"],
    "cholesterol_total": [r"\b(total\s+cholesterol|cholesterol[,\s]+total)\b[^\d]*(\d+\.?\d*)"],
    "cholesterol_ldl": [r"\b(ldl|ldl[- ]cholesterol|low\s+density\s+lipoprotein)\b[^\d]*(\d+\.?\d*)"],
    "cholesterol_hdl": [r"\b(hdl|hdl[- ]cholesterol|high\s+density\s+lipoprotein)\b[^\d]*(\d+\.?\d*)"],
    "triglycerides": [r"\b(triglyceride[s]?|trig)\b[^\d]*(\d+\.?\d*)"],
    "glucose_fasting": [r"\b(fasting\s+glucose|glucose[,\s]+fasting|glucose)\b[^\d]*(\d+\.?\d*)"],
    "hba1c": [r"\b(hba1c|a1c|glycated\s+hemoglobin)\b[^\d]*(\d+\.?\d*)"],
    "creatinine": [r"\b(serum\s+creatinine|creatinine)\b[^\d]*(\d+\.?\d*)"],
    "bun": [r"\b(bun|blood\s+urea\s+nitrogen)\b[^\d]*(\d+\.?\d*)"],
    "alt": [r"\b(alt|alanine\s+aminotransferase|sgpt)\b[^\d]*(\d+\.?\d*)"],
    "tsh": [r"\b(tsh|thyroid\s+stimulating\s+hormone)\b[^\d]*(\d+\.?\d*)"],
    "vitamin_d": [r"\b(vitamin\s+d|25[- ]hydroxy\s+vitamin\s+d|vit\s+d)\b[^\d]*(\d+\.?\d*)"]
}


class ReportDecoderAgent:
    """Decodes and explains laboratory test values in everyday language."""

    def __init__(self):
        self.knowledge = self._load_knowledge()
        self.tests_db = self.knowledge.get("tests", {})

    def _load_knowledge(self) -> Dict[str, Any]:
        try:
            if os.path.exists(DATA_PATH):
                with open(DATA_PATH, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    def parse_report_text(self, text: str) -> Dict[str, Any]:
        """
        Extracts biomarkers and builds a plain-English explanation.
        """
        extracted = []
        found_test_keys = set()

        for test_key, patterns in TEST_PATTERNS.items():
            if test_key in found_test_keys:
                continue
            for pattern in patterns:
                match = re.search(pattern, text, flags=re.IGNORECASE)
                if match:
                    try:
                        val = float(match.group(2) if len(match.groups()) >= 2 else match.group(1))
                        item_info = self._analyze_test_value(test_key, val)
                        if item_info:
                            extracted.append(item_info)
                            found_test_keys.add(test_key)
                            break
                    except (ValueError, IndexError):
                        continue

        if not extracted:
            # If no automated biomarker match, generate general analysis guidance
            return {
                "detected_count": 0,
                "biomarkers": [],
                "summary": (
                    "No recognized standard blood test biomarkers (like WBC, Hemoglobin, Cholesterol, "
                    "Glucose, HbA1c, TSH) were detected in the text. "
                    "You can try typing lines such as:\n"
                    "- `Hemoglobin: 11.2 g/dL`\n"
                    "- `Total Cholesterol: 220 mg/dL`\n"
                    "- `HbA1c: 6.1%`\n"
                    "Or select one of the pre-loaded sample lab reports."
                ),
                "questions_for_doctor": [
                    "What do each of the flagged values in this report mean for my overall health?",
                    "Are any of these findings urgent, or should we monitor them over time?",
                    "Could my diet, sleep, or recent hydration level have influenced these results?"
                ]
            }

        # Aggregate questions
        all_questions = []
        for item in extracted:
            for q in item.get("questions_for_doctor", []):
                if q not in all_questions:
                    all_questions.append(q)

        return {
            "detected_count": len(extracted),
            "biomarkers": extracted,
            "summary": self._build_plain_summary(extracted),
            "questions_for_doctor": all_questions[:6]
        }

    def _analyze_test_value(self, test_key: str, value: float) -> Optional[Dict[str, Any]]:
        info = self.tests_db.get(test_key)
        if not info:
            return None

        status = "Within Standard Range"
        status_color = "green"
        indicator = "normal"

        # Numerical bounds evaluation
        if test_key == "wbc":
            if value < 4.5:
                status, status_color, indicator = "Below Standard Range", "blue", "low"
            elif value > 11.0:
                status, status_color, indicator = "Above Standard Range", "amber", "high"
        elif test_key == "rbc":
            if value < 4.2:
                status, status_color, indicator = "Below Standard Range", "blue", "low"
            elif value > 5.9:
                status, status_color, indicator = "Above Standard Range", "amber", "high"
        elif test_key == "hemoglobin":
            if value < 12.0:
                status, status_color, indicator = "Below Standard Range (Mild Low)", "blue", "low"
            elif value > 17.5:
                status, status_color, indicator = "Above Standard Range", "amber", "high"
        elif test_key == "hematocrit":
            if value < 36.0:
                status, status_color, indicator = "Below Standard Range", "blue", "low"
            elif value > 50.0:
                status, status_color, indicator = "Above Standard Range", "amber", "high"
        elif test_key == "platelets":
            if value < 150:
                status, status_color, indicator = "Below Standard Range", "blue", "low"
            elif value > 450:
                status, status_color, indicator = "Above Standard Range", "amber", "high"
        elif test_key == "cholesterol_total":
            if value >= 240:
                status, status_color, indicator = "High (Desirable < 200)", "rose", "high"
            elif value >= 200:
                status, status_color, indicator = "Borderline High (Desirable < 200)", "amber", "borderline"
        elif test_key == "cholesterol_ldl":
            if value >= 160:
                status, status_color, indicator = "High (Optimal < 100)", "rose", "high"
            elif value >= 100:
                status, status_color, indicator = "Above Optimal Range (Optimal < 100)", "amber", "high"
        elif test_key == "cholesterol_hdl":
            if value < 40:
                status, status_color, indicator = "Lower Than Recommended (> 40-50 desirable)", "amber", "low"
        elif test_key == "triglycerides":
            if value >= 200:
                status, status_color, indicator = "Elevated (Normal < 150)", "rose", "high"
            elif value >= 150:
                status, status_color, indicator = "Borderline High (Normal < 150)", "amber", "borderline"
        elif test_key == "glucose_fasting":
            if value < 70:
                status, status_color, indicator = "Low (Standard 70-99)", "blue", "low"
            elif value >= 126:
                status, status_color, indicator = "Elevated Fasting Range (Standard 70-99)", "rose", "high"
            elif value >= 100:
                status, status_color, indicator = "Borderline Fasting Range (Standard 70-99)", "amber", "borderline"
        elif test_key == "hba1c":
            if value >= 6.5:
                status, status_color, indicator = "Elevated Glycemic Index (Standard < 5.7%)", "rose", "high"
            elif value >= 5.7:
                status, status_color, indicator = "Borderline / Prediabetes Benchmark (5.7 - 6.4%)", "amber", "borderline"
        elif test_key == "creatinine":
            if value > 1.3:
                status, status_color, indicator = "Above Standard Range (Standard 0.6-1.3)", "amber", "high"
            elif value < 0.6:
                status, status_color, indicator = "Below Standard Range", "blue", "low"
        elif test_key == "bun":
            if value > 20:
                status, status_color, indicator = "Above Standard Range (Standard 7-20)", "amber", "high"
        elif test_key == "alt":
            if value > 56:
                status, status_color, indicator = "Elevated Liver Enzyme (Standard 7-56)", "amber", "high"
        elif test_key == "tsh":
            if value > 4.5:
                status, status_color, indicator = "Above Standard Range (Standard 0.4-4.5)", "amber", "high"
            elif value < 0.4:
                status, status_color, indicator = "Below Standard Range (Standard 0.4-4.5)", "blue", "low"
        elif test_key == "vitamin_d":
            if value < 20:
                status, status_color, indicator = "Deficient Range (Optimal 30-100)", "rose", "low"
            elif value < 30:
                status, status_color, indicator = "Suboptimal / Insufficient (Optimal 30-100)", "amber", "low"

        return {
            "key": test_key,
            "name": info["name"],
            "value": value,
            "unit": info.get("unit", ""),
            "standard_range": info.get("standard_range", ""),
            "status": status,
            "status_color": status_color,
            "indicator": indicator,
            "analogy": info.get("analogy", ""),
            "summary": info.get("summary", ""),
            "lifestyle_factors": info.get("lifestyle_factors", ""),
            "questions_for_doctor": info.get("questions_for_doctor", [])
        }

    def _build_plain_summary(self, extracted: List[Dict[str, Any]]) -> str:
        outside_count = sum(1 for item in extracted if item["indicator"] != "normal")
        normal_count = len(extracted) - outside_count

        lines = [
            f"Analyzed **{len(extracted)} lab indicator(s)**: **{normal_count} within standard range**, and **{outside_count} with values outside standard benchmarks**.",
            "",
            "### 💡 Key Takeaways in Plain English:"
        ]

        for item in extracted:
            icon = "✅" if item["indicator"] == "normal" else "🔍"
            lines.append(f"- **{item['name']} ({item['value']} {item['unit']})**: {icon} *{item['status']}*")
            lines.append(f"  - **Everyday Analogy:** {item['analogy']}")
            if item["lifestyle_factors"]:
                lines.append(f"  - **Non-Disease Factors:** {item['lifestyle_factors']}")

        lines.append("")
        lines.append("Remember: Laboratory 'reference ranges' represent 95% of a healthy reference population. Small deviations are common and don't automatically mean an illness is present. Share these questions with your physician at your next visit.")

        return "\n".join(lines)
