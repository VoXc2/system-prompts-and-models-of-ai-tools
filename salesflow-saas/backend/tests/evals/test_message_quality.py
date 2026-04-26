"""Tests that generated messages meet quality standards."""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dealix_gtm_os.agents.message_generation_agent import MessageGenerationAgent

async def test_message_quality():
    agent = MessageGenerationAgent()
    
    cases = [
        {"name": "وكالة تسويق", "sector": "agency", "channel": "email"},
        {"name": "شركة عقار", "sector": "real_estate", "channel": "email"},
        {"name": "عيادة", "sector": "saas", "channel": "whatsapp_warm"},
    ]
    
    passed = 0
    for case in cases:
        msg = await agent.run(case)
        issues = []
        
        if case["name"] not in msg.get("body", ""):
            issues.append("company name not in body")
        if "إيقاف" not in msg.get("stop_condition", "") and "إيقاف" not in msg.get("body", ""):
            issues.append("no opt-out")
        if not msg.get("approval_required"):
            issues.append("approval not required")
        if not msg.get("follow_up_24h"):
            issues.append("no 24h follow-up")
        if not msg.get("follow_up_72h"):
            issues.append("no 72h follow-up")
        if len(msg.get("body", "")) < 50:
            issues.append("body too short")
        if len(msg.get("body", "").split()) > 300:
            issues.append("body too long")
        
        if issues:
            print(f"  ❌ {case['name']}: {', '.join(issues)}")
        else:
            passed += 1
            print(f"  ✅ {case['name']}: personalized, opt-out, approval, follow-ups")
    
    print(f"\nMessage quality: {passed}/{len(cases)} passed")
    assert passed == len(cases)

if __name__ == "__main__":
    print("=== Message Quality Tests ===")
    asyncio.run(test_message_quality())
    print("\n✅ ALL MESSAGE QUALITY TESTS PASSED")
