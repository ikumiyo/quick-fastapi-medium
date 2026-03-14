class OpenAIClient:
    """OpenAI SDK 占位封装。"""

    def chat(self, prompt: str) -> str:
        raise NotImplementedError("请在此接入 OpenAI SDK，并实现统一的 AI 能力封装")
