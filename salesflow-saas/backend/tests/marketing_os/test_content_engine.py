import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dealix_marketing_os.engines.content_engine import generate_daily_content

def test_content_generation():
    for day in range(1, 6):
        c = generate_daily_content(day_number=day)
        assert c["linkedin"]["post"], f"Day {day}: no LinkedIn post"
        assert c["x"]["post"], f"Day {day}: no X post"
        assert c["instagram_story"]["text"], f"Day {day}: no IG story"
        assert c["no_auto_post"] == True, "Must not auto-post"
        assert "مضمون" not in c["linkedin"]["post"], "No fake claims in LinkedIn"
        assert "guaranteed" not in c["linkedin"]["post"].lower(), "No guaranteed claims"
        print(f"  ✅ Day {day}: content generated, safe, no auto-post")
    print("\n✅ ALL CONTENT TESTS PASSED")

if __name__ == "__main__":
    test_content_generation()
