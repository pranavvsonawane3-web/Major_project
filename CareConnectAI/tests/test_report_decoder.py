"""
Tests for CareConnect AI Medical Report Simplifier
"""

from app.agent.report_decoder import ReportDecoderAgent

def test_cbc_parsing():
    decoder = ReportDecoderAgent()
    sample = "WBC: 12.4 x10^3/uL\nHemoglobin: 11.2 g/dL\nPlatelets: 280 x10^3/uL"
    result = decoder.parse_report_text(sample)
    assert result["detected_count"] >= 2
    keys = [b["key"] for b in result["biomarkers"]]
    assert "wbc" in keys
    assert "hemoglobin" in keys

    # Verify plain analogies and questions are attached
    wbc_item = next(b for b in result["biomarkers"] if b["key"] == "wbc")
    assert "security guards" in wbc_item["analogy"].lower()
    assert len(wbc_item["questions_for_doctor"]) > 0

def test_lipid_parsing():
    decoder = ReportDecoderAgent()
    sample = "Total Cholesterol: 245 mg/dL\nLDL Cholesterol: 165 mg/dL\nTriglycerides: 210 mg/dL"
    result = decoder.parse_report_text(sample)
    assert result["detected_count"] >= 3
    ldl_item = next(b for b in result["biomarkers"] if b["key"] == "cholesterol_ldl")
    assert ldl_item["status_color"] in ["rose", "amber"]
    assert "Optimal < 100" in ldl_item["status"]
