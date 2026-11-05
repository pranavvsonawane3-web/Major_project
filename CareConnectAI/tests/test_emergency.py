"""
Tests for CareConnect AI Emergency Red-Flag Detection
"""

from app.agent.emergency_agent import EmergencyAgent

def test_chest_pain_triggers_emergency():
    agent = EmergencyAgent()
    res = agent.check_for_emergency("I am having severe crushing chest pain and left arm numbness")
    assert res is not None
    assert res["is_emergency"] is True
    assert "chest pain" in res["matched_red_flags"]
    assert "911" in res["formatted_message"]

def test_stroke_signs_trigger_emergency():
    agent = EmergencyAgent()
    res = agent.check_for_emergency("My father has sudden facial droop and slurred speech")
    assert res is not None
    assert res["is_emergency"] is True
    assert any("facial droop" in f or "slurred speech" in f for f in res["matched_red_flags"])

def test_mental_health_crisis_triggers_988():
    agent = EmergencyAgent()
    res = agent.check_for_emergency("I feel hopeless and want to end my life")
    assert res is not None
    assert res["is_emergency"] is True
    assert "988" in res["formatted_message"]
    assert "CRISIS" in res["formatted_message"]

def test_routine_question_does_not_trigger_emergency():
    agent = EmergencyAgent()
    res = agent.check_for_emergency("What does fasting blood glucose mean?")
    assert res is None
