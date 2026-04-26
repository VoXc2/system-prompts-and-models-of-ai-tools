"""Token counter — estimates tokens before sending to avoid waste."""
import re

def estimate_tokens(text: str) -> int:
    """Rough token estimate: ~4 chars per token for mixed Arabic/English."""
    if not text:
        return 0
    words = len(re.findall(r'\S+', text))
    chars = len(text)
    return max(words, chars // 4)

def check_budget(tokens: int, max_tokens: int) -> bool:
    """Returns True if within budget."""
    return tokens <= max_tokens

def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Truncates text to fit within token budget."""
    estimated = estimate_tokens(text)
    if estimated <= max_tokens:
        return text
    ratio = max_tokens / estimated
    cut_at = int(len(text) * ratio * 0.9)
    return text[:cut_at] + "\n[truncated]"
