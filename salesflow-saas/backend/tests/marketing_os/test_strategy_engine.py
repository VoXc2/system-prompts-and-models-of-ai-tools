import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dealix_marketing_os.engines.strategy_engine import generate_daily_strategy

def test_strategy():
    for day in range(1, 8):
        s = generate_daily_strategy(day_number=day)
        assert s["target_segment"], f"Day {day}: no target segment"
        assert s["primary_offer"], f"Day {day}: no offer"
        assert s["priority_channels"], f"Day {day}: no channels"
        assert s["daily_minimum"]["touches"] >= 10, "Min 10 touches"
        print(f"  ✅ Day {day}: {s['target_segment']} → {s['primary_offer']}")
    print("\n✅ ALL STRATEGY TESTS PASSED")

if __name__ == "__main__":
    test_strategy()
