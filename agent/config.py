import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
AGENT_DIR = Path(__file__).resolve().parent
DEFAULT_PROVIDER = "groq"
DEFAULT_MODEL = "openai/gpt-oss-120b"
DEFAULT_MAX_TOOL_CALLS = 8


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    api_key: str | None
    max_tool_calls: int


class GroqChatProvider:
    def __init__(self, config: LLMConfig):
        if not config.api_key:
            raise RuntimeError("GROQ_API_KEY is required to run the agent.")
        from groq import Groq

        self.config = config
        self.client = Groq(api_key=config.api_key)

    def create_completion(self, messages: list, tools: list):
        return self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )


def _read_int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def get_llm_config() -> LLMConfig:
    load_dotenv(AGENT_DIR / ".env")
    provider = os.getenv("AQUANEXUS_LLM_PROVIDER", DEFAULT_PROVIDER).lower()
    return LLMConfig(
        provider=provider,
        model=os.getenv("AQUANEXUS_LLM_MODEL", DEFAULT_MODEL),
        api_key=os.getenv("GROQ_API_KEY"),
        max_tool_calls=_read_int_env("AQUANEXUS_MAX_TOOL_CALLS", DEFAULT_MAX_TOOL_CALLS),
    )


def get_chat_provider(config: LLMConfig | None = None):
    config = config or get_llm_config()
    if config.provider == "groq":
        return GroqChatProvider(config)
    raise ValueError(f"Unsupported LLM provider: {config.provider}")
