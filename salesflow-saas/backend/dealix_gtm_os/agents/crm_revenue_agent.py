from dealix_gtm_os.agents.base_agent import BaseAgent

STATUS_FLOW = ["new", "researched", "qualified", "message_ready", "approved", "sent", "replied", "interested", "demo_booked", "proposal_sent", "payment_sent", "paid", "won", "lost", "partner", "stop"]

class CRMRevenueAgent(BaseAgent):
    name = "crm_revenue"
    description = "Manages lead/deal status transitions"

    async def run(self, input_data: dict) -> dict:
        current = input_data.get("status", "new")
        event = input_data.get("event", "")
        next_status = current
        next_action = ""
        if event == "researched": next_status, next_action = "researched", "score and qualify"
        elif event == "qualified": next_status, next_action = "qualified", "generate message"
        elif event == "message_ready": next_status, next_action = "message_ready", "send to approval"
        elif event == "approved": next_status, next_action = "approved", "send message"
        elif event == "sent": next_status, next_action = "sent", "wait for reply"
        elif event == "replied_interested": next_status, next_action = "interested", "book demo within 24h"
        elif event == "demo_booked": next_status, next_action = "demo_booked", "prepare demo"
        elif event == "demo_done": next_status, next_action = "proposal_sent", "send payment link"
        elif event == "payment_sent": next_status, next_action = "payment_sent", "wait for payment"
        elif event == "paid": next_status, next_action = "paid", "start onboarding"
        elif event == "lost": next_status, next_action = "lost", "log reason"
        elif event == "stop": next_status, next_action = "stop", "remove from list"
        return {"previous_status": current, "new_status": next_status, "next_action": next_action}
