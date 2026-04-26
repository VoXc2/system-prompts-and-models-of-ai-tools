from dealix_gtm_os.agents.base_agent import BaseAgent

class LearningAgent(BaseAgent):
    name = "learning"
    description = "Analyzes results and suggests improvements"

    async def run(self, input_data: dict) -> dict:
        sent = input_data.get("total_sent", 0)
        replies = input_data.get("total_replies", 0)
        demos = input_data.get("total_demos", 0)
        payments = input_data.get("total_payments", 0)
        best_sector = input_data.get("best_sector", "unknown")
        best_channel = input_data.get("best_channel", "unknown")
        reply_rate = (replies / sent * 100) if sent > 0 else 0
        demo_rate = (demos / replies * 100) if replies > 0 else 0
        recommendations = []
        if reply_rate < 3 and sent >= 30: recommendations.append("غيّر الرسالة أو القطاع — reply rate أقل من 3%")
        if demo_rate < 20 and replies >= 5: recommendations.append("غيّر CTA — demos أقل من 20% من الردود")
        if best_sector != "unknown": recommendations.append(f"ركّز على {best_sector} — أفضل أداء")
        if best_channel != "unknown": recommendations.append(f"ضاعف {best_channel} — أفضل قناة")
        if not recommendations: recommendations.append("استمر — البيانات ما زالت قليلة")
        return {"reply_rate": round(reply_rate, 1), "demo_rate": round(demo_rate, 1), "recommendations": recommendations}
