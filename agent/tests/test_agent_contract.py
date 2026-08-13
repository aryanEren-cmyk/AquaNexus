import sys
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent import run_agent  # noqa: E402
from config import LLMConfig  # noqa: E402


class FakeChatProvider:
    def create_completion(self, messages: list, tools: list):
        message = SimpleNamespace(
            content="Mock agent response.",
            tool_calls=None,
        )
        choice = SimpleNamespace(message=message)
        return SimpleNamespace(choices=[choice])


class AgentContractTests(TestCase):
    def test_agent_response_contract(self):
        config = LLMConfig(
            provider="groq",
            model="test-model",
            api_key=None,
            max_tool_calls=8,
        )

        with patch("agent.get_llm_config", return_value=config):
            result = run_agent("Is the Arabian Sea warm?", chat_provider=FakeChatProvider())

        self.assertEqual(set(result.keys()), {"text", "chart_data", "map_data"})
        self.assertIsInstance(result["text"], str)
        self.assertIsNone(result["chart_data"])
        self.assertIsNone(result["map_data"])
