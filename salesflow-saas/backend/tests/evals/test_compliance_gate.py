"""Tests that compliance gate blocks all prohibited actions."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dealix_gtm_os.guardrails.output_validator import validate_channel_action, validate_output

def test_prohibited_actions():
    prohibited_cases = [
        ("linkedin", "scraping"),
        ("linkedin", "auto_dm"),
        ("linkedin", "auto_connect"),
        ("whatsapp", "cold_blast"),
        ("whatsapp", "mass_send"),
        ("instagram", "mass_dm"),
        ("instagram", "scraping"),
        ("x", "auto_mention"),
        ("tiktok", "dm_scraping"),
        ("tiktok", "mass_dm"),
    ]
    passed = 0
    for channel, action in prohibited_cases:
        result = validate_channel_action(channel, action)
        if not result["allowed"]:
            passed += 1
            print(f"  ✅ {channel}/{action} → BLOCKED")
        else:
            print(f"  ❌ {channel}/{action} → NOT BLOCKED (FAIL)")
    
    print(f"\nProhibited actions: {passed}/{len(prohibited_cases)} blocked")
    assert passed == len(prohibited_cases), f"Only {passed}/{len(prohibited_cases)} blocked"

def test_allowed_actions():
    allowed_cases = [
        ("email", "send_message"),
        ("linkedin", "research"),
        ("whatsapp", "warm_message"),
        ("x", "post"),
    ]
    passed = 0
    for channel, action in allowed_cases:
        result = validate_channel_action(channel, action)
        if result["allowed"]:
            passed += 1
            print(f"  ✅ {channel}/{action} → ALLOWED")
        else:
            print(f"  ❌ {channel}/{action} → BLOCKED (FAIL)")
    
    print(f"\nAllowed actions: {passed}/{len(allowed_cases)} allowed")
    assert passed == len(allowed_cases)

def test_forbidden_claims():
    bad_texts = [
        "نتائج مضمونة 100% لكل العملاء",
        "Dealix is SOC 2 compliant and ISO 27001 certified",
        "ربح مضمون من أول يوم بدون أي جهد",
    ]
    for text in bad_texts:
        result = validate_output(text)
        assert not result["valid"], f"Should have blocked: {text[:30]}..."
        print(f"  ✅ Blocked: {text[:40]}...")
    
    good_text = "Dealix يساعد في تحسين متابعة العملاء. نبدأ بـ pilot 499 ريال مع ضمان استرداد."
    result = validate_output(good_text)
    assert result["valid"], "Should have allowed safe text"
    print(f"  ✅ Allowed safe text")

if __name__ == "__main__":
    print("=== Prohibited Actions ===")
    test_prohibited_actions()
    print("\n=== Allowed Actions ===")
    test_allowed_actions()
    print("\n=== Forbidden Claims ===")
    test_forbidden_claims()
    print("\n✅ ALL COMPLIANCE TESTS PASSED")
