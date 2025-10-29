"""Tests for the tool mock generator service."""
import json
from types import SimpleNamespace

try:
    import pytest  # type: ignore[import]
except ImportError:  # pragma: no cover
    pytest = None  # type: ignore

if pytest is None:  # pragma: no cover
    class _PytestShim:
        """Minimal shim so type checkers accept pytest usage when missing."""

        class mark:  # type: ignore[no-redef]
            @staticmethod
            def asyncio(func):
                return func

    pytest = _PytestShim()  # type: ignore

from app.models.tool_mock_generation import ToolMockGenerationRequest
from app.services.tool_mock_generator import ToolMockGeneratorService
from app.services import tool_mock_generator


@pytest.mark.asyncio
async def test_generate_mock_config_success(monkeypatch):
    """Service returns success when LLM output is valid JSON."""

    async def fake_call_model(**kwargs):
        payload = {
            "enabled": True,
            "response_type": "static",
            "static_response": {"success": True},
            "latency_ms": {"min": 120, "max": 200},
        }
        return {
            "status": "success",
            "output": json.dumps(payload),
            "metrics": {"prompt_tokens": 10},
        }

    monkeypatch.setattr(tool_mock_generator.LLMService, "call_model", fake_call_model)

    tool = SimpleNamespace(
        name="calendar_search",
        description="查询日程的工具",
        parameters={"type": "object", "properties": {}},
        example_call=None,
        mock_responses=None,
    )
    model = SimpleNamespace(name="MockModel")
    request = ToolMockGenerationRequest(model_id=1)

    result = await ToolMockGeneratorService.generate_mock_config(tool, model, request)

    assert result.status == "success"
    assert result.mock_config is not None
    assert result.mock_config["enabled"] is True


@pytest.mark.asyncio
async def test_generate_mock_config_invalid_output(monkeypatch):
    """Service reports invalid_output when JSON cannot be parsed."""

    async def fake_call_model(**kwargs):
        return {
            "status": "success",
            "output": "Please see the configuration above.",
            "metrics": {"prompt_tokens": 10},
        }

    monkeypatch.setattr(tool_mock_generator.LLMService, "call_model", fake_call_model)

    tool = SimpleNamespace(
        name="calendar_search",
        description="查询日程的工具",
        parameters={"type": "object", "properties": {}},
        example_call=None,
        mock_responses=None,
    )
    model = SimpleNamespace(name="MockModel")
    request = ToolMockGenerationRequest(model_id=1)

    result = await ToolMockGeneratorService.generate_mock_config(tool, model, request)

    assert result.status == "invalid_output"
    assert result.mock_config is None
    assert result.validation_error is not None
