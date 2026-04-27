import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dealix_marketing_os.engines.content_engine import generate_daily_content
from dealix_marketing_os.engines.partner_marketing_engine import generate_partner_assets
from dealix_marketing_os.engines.social_engine import generate_social_plan

def test_no_fake_claims():
    for day in range(1, 6):
        c = generate_daily_content(day_number=day)
        for text in [c["linkedin"]["post"], c["x"]["post"]]:
            for bad in ["مضمون", "guaranteed", "100%", "بدون منافس"]:
                assert bad not in text.lower(), f"Fake claim '{bad}' in content"
    print("  ✅ No fake claims in content")

def test_partner_safety():
    p = generate_partner_assets()
    assert p.get("partner_one_pager",{}).get("safe_wording") == True, "Partner assets must use safe wording"
    assert p.get("partner_one_pager",{}).get("no_guaranteed_profit") == True, "Must not guarantee profit"
    assert p.get("partner_one_pager",{}).get("payout_after_verified_payment") == True, "Payout after payment only"
    print("  ✅ Partner assets safe")

def test_social_prohibited():
    s = generate_social_plan()
    assert "linkedin_scraping" in s["prohibited"], "LinkedIn scraping must be prohibited"
    assert "whatsapp_cold_blast" in s["prohibited"], "WhatsApp blast must be prohibited"
    assert s["no_auto_post"] == True, "Must not auto-post"
    print("  ✅ Social prohibited actions enforced")

if __name__ == "__main__":
    test_no_fake_claims()
    test_partner_safety()
    test_social_prohibited()
    print("\n✅ ALL MARKETING SAFETY TESTS PASSED")
