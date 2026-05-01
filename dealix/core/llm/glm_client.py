"""
GLM (Z.ai / BigModel) client — strong for Arabic + Chinese + bulk work.
عميل GLM — قوي للعربية والصينية والمهام الكثيرة.
"""

from __future__ import annotations

from core.llm.openai_compat import OpenAICompatClient


class GLMClient(OpenAICompatClient):
    """GLM-4 via BigModel API (OpenAI-compatible)."""

    provider_name = "glm"

    def __init__(
        self,
        api_key: str,
        model: str = "glm-4",
        base_url: str = "https://open.bigmodel.cn/api/paas/v4",
        timeout: int = 60,
    ) -> None:
        super().__init__(api_key=api_key, model=model, base_url=base_url, timeout=timeout)
