"""LLM Router — routes to right model, enforces budgets, uses cache."""
import json
import os
import time
import yaml
from pathlib import Path
from typing import Optional

from dealix_gtm_os.ai.token_counter import estimate_tokens, truncate_to_budget
from dealix_gtm_os.ai.response_cache import get_cached, set_cached
from dealix_gtm_os.ai.prompt_registry import get_prompt

_config_path = Path(__file__).parent.parent / "config" / "ai_budget.yaml"
_config = {}
if _config_path.exists():
    with open(_config_path) as f:
        _config = yaml.safe_load(f) or {}

_daily_cost = 0.0
_daily_requests = 0
_daily_reset = time.time()

def _check_daily_budget() -> bool:
    global _daily_cost, _daily_requests, _daily_reset
    if time.time() - _daily_reset > 86400:
        _daily_cost = 0.0
        _daily_requests = 0
        _daily_reset = time.time()
    budget = _config.get("daily_budget", {})
    if _daily_cost >= budget.get("max_cost_sar", 10.0):
        return False
    if _daily_requests >= budget.get("max_requests", 500):
        return False
    return True

def _get_agent_config(agent_name: str) -> dict:
    return _config.get("agent_budgets", {}).get(agent_name, {"model_tier": "mid", "max_output_tokens": 500, "cache_ttl_hours": 24})

async def route_llm_call(agent_name: str, prompt_name: str, input_data: dict, **prompt_kwargs) -> str:
    """Main entry point. Routes to correct model with budget/cache."""
    global _daily_cost, _daily_requests

    agent_cfg = _get_agent_config(agent_name)
    cache_ttl = agent_cfg.get("cache_ttl_hours", 24)

    if cache_ttl > 0:
        cached = get_cached(agent_name, input_data, cache_ttl)
        if cached:
            return json.dumps(cached, ensure_ascii=False)

    if not _check_daily_budget():
        return json.dumps({"error": "Daily AI budget exceeded", "budget_hit": True})

    groq_key = os.environ.get("GROQ_API_KEY", "")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")

    if not groq_key and not anthropic_key:
        from dealix_gtm_os.agents.llm_client import call_llm
        result = await call_llm("", context=input_data)
        _daily_requests += 1
        if cache_ttl > 0:
            try:
                set_cached(agent_name, input_data, json.loads(result))
            except Exception:
                pass
        return result

    model_tier = agent_cfg.get("model_tier", "mid")
    models = _config.get("models", {})
    model_cfg = models.get(model_tier, models.get("mid", {}))
    model_id = model_cfg.get("id", "groq/llama-3.3-70b-versatile")
    max_tokens = agent_cfg.get("max_output_tokens", 500)

    try:
        system_prompt, user_prompt = get_prompt(prompt_name, **prompt_kwargs)
    except (ValueError, KeyError):
        system_prompt = "أنت Dealix AI."
        user_prompt = json.dumps(input_data, ensure_ascii=False)

    user_prompt = truncate_to_budget(user_prompt, 2000)

    if model_id.startswith("groq/") and groq_key:
        result = await _call_groq(groq_key, model_id.replace("groq/", ""), system_prompt, user_prompt, max_tokens)
    elif model_id.startswith("anthropic/") and anthropic_key:
        result = await _call_anthropic(anthropic_key, model_id.replace("anthropic/", ""), system_prompt, user_prompt, max_tokens)
    elif groq_key:
        result = await _call_groq(groq_key, "llama-3.3-70b-versatile", system_prompt, user_prompt, max_tokens)
    else:
        from dealix_gtm_os.agents.llm_client import call_llm
        result = await call_llm("", context=input_data)

    _daily_requests += 1
    input_tokens = estimate_tokens(system_prompt + user_prompt)
    output_tokens = estimate_tokens(result)
    cost_input = input_tokens / 1000 * model_cfg.get("cost_per_1k_input", 0.001)
    cost_output = output_tokens / 1000 * model_cfg.get("cost_per_1k_output", 0.002)
    _daily_cost += (cost_input + cost_output) * 3.75

    if cache_ttl > 0:
        try:
            set_cached(agent_name, input_data, json.loads(result))
        except Exception:
            pass

    return result

async def _call_groq(api_key: str, model: str, system: str, user: str, max_tokens: int) -> str:
    import httpx
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": model, "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}], "max_tokens": max_tokens, "temperature": 0.3, "response_format": {"type": "json_object"}},
        )
        data = resp.json()
        return data.get("choices", [{}])[0].get("message", {}).get("content", "{}")

async def _call_anthropic(api_key: str, model: str, system: str, user: str, max_tokens: int) -> str:
    import httpx
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"},
            json={"model": model, "system": system, "messages": [{"role": "user", "content": user}], "max_tokens": max_tokens},
        )
        data = resp.json()
        content = data.get("content", [{}])
        return content[0].get("text", "{}") if content else "{}"

def get_cost_report() -> dict:
    return {"daily_cost_sar": round(_daily_cost, 4), "daily_requests": _daily_requests, "budget_remaining_sar": round(max(0, _config.get("daily_budget", {}).get("max_cost_sar", 10) - _daily_cost), 4)}
