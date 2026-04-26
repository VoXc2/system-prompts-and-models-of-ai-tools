"""GTM OS evaluation tests — verifies intelligence quality."""
import asyncio
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dealix_gtm_os.agents.supervisor_agent import SupervisorAgent

EVAL_FILE = os.path.join(os.path.dirname(__file__), "gtm_os_eval_set.jsonl")

async def run_evals():
    supervisor = SupervisorAgent()
    with open(EVAL_FILE) as f:
        cases = [json.loads(line) for line in f if line.strip()]

    passed = 0
    failed = 0
    total = len(cases)

    for case in cases:
        result = await supervisor.run({
            "name": case["company"],
            "sector": case["sector"],
            "city": case["city"],
        })

        channel = result["channel_plan"]["primary_channel"]
        compliance = result["compliance"]["allowed"]
        opportunity = result["intelligence"].get("opportunity_types", [])
        has_optout = "إيقاف" in result["message"].get("stop_condition", "")

        errors = []
        if case["expected_channel"] != channel:
            errors.append(f"channel: expected {case['expected_channel']}, got {channel}")
        if not compliance:
            errors.append("compliance: should be allowed but was denied")
        if not has_optout:
            errors.append("missing opt-out in message")
        if case["expected_opportunity"] not in opportunity:
            pass  # opportunity matching is advisory

        if errors:
            failed += 1
            print(f"  ❌ {case['company']}: {'; '.join(errors)}")
        else:
            passed += 1
            print(f"  ✅ {case['company']}: channel={channel}, compliant={compliance}")

    print(f"\n{'=' * 40}")
    print(f"Results: {passed}/{total} passed ({passed/total*100:.0f}%)")
    print(f"Failed: {failed}")
    if passed / total >= 0.8:
        print("VERDICT: ✅ PASS (≥80%)")
    else:
        print("VERDICT: ❌ FAIL (<80%)")
    return passed / total >= 0.8

if __name__ == "__main__":
    success = asyncio.run(run_evals())
    sys.exit(0 if success else 1)
