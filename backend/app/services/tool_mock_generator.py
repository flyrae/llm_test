"""Service for generating tool mock configurations via LLM."""
import json
import logging
import textwrap
import re
from typing import Any, Dict, List, Optional

from app.models.model_config import ModelConfigDB
from app.models.tool_definition import ToolDefinitionDB
from app.models.tool_mock_generation import (
    MockScenario,
    ToolMockGenerationRequest,
    ToolMockGenerationResponse,
)
from app.services.llm_service import LLMService
from app.services.mock_tool_executor import MockToolExecutor

logger = logging.getLogger(__name__)


class ToolMockGeneratorService:
    """Generate mock configuration for tools by delegating to an LLM."""

    @staticmethod
    async def generate_mock_config(
        tool: ToolDefinitionDB,
        model_config: ModelConfigDB,
        request: ToolMockGenerationRequest,
    ) -> ToolMockGenerationResponse:
        """Generate mock configuration for a tool.

        Handles prompt construction, LLM invocation, JSON extraction, and validation.
        """

        system_prompt = ToolMockGeneratorService._build_system_prompt(request.language)
        user_prompt = ToolMockGeneratorService._build_user_prompt(tool, request)
        logger.info("🧪 Generating mock config for tool %s via model %s", tool.name, model_config.name)

        llm_result = await LLMService.call_model(
            model_config=model_config,
            content=[{"type": "text", "text": user_prompt}],
            system_prompt=system_prompt,
            params={"temperature": 0.2},
            stream=False,
        )

        if llm_result.get("status") != "success":
            logger.error("Mock generation failed: %s", llm_result.get("error_message"))
            return ToolMockGenerationResponse(
                status="error",
                mock_config=None,
                validation_error=llm_result.get("error_message"),
                raw_output=llm_result.get("output"),
                metrics=llm_result.get("metrics"),
                saved=False,
            )

        raw_output = llm_result.get("output", "")
        logger.debug("Mock generation raw output: %s", raw_output)

        mock_config = ToolMockGeneratorService._extract_json_block(raw_output)
        if mock_config is None:
            logger.error("Unable to parse JSON from LLM output")
            return ToolMockGenerationResponse(
                status="invalid_output",
                mock_config=None,
                validation_error="LLM output is not valid JSON",
                raw_output=raw_output,
                metrics=llm_result.get("metrics"),
                saved=False,
            )

        is_valid, validation_error = MockToolExecutor.validate_mock_config(mock_config)
        if not is_valid:
            logger.error("Generated mock config did not pass validation: %s", validation_error)
            return ToolMockGenerationResponse(
                status="validation_failed",
                mock_config=mock_config,
                validation_error=validation_error,
                raw_output=raw_output,
                metrics=llm_result.get("metrics"),
                saved=False,
            )

        return ToolMockGenerationResponse(
            status="success",
            mock_config=mock_config,
            validation_error=None,
            raw_output=raw_output,
            metrics=llm_result.get("metrics"),
            saved=False,
        )

    @staticmethod
    def _build_system_prompt(language: Optional[str]) -> str:
        """Build the system prompt in the requested language."""

        lang = (language or "zh").lower()
        if lang.startswith("zh"):
            return textwrap.dedent(
                """
                你是一名擅长为工具生成模拟配置的专家，需要严格输出 JSON。
                请基于用户提供的信息构建符合要求的 mock 配置，务必只输出 JSON 对象。
                """
            ).strip()

        return textwrap.dedent(
            """
            You are an expert mock configuration generator for developer tools.
            Always respond with a single JSON object that adheres to the requested schema.
            """
        ).strip()

    @staticmethod
    def _build_user_prompt(
        tool: ToolDefinitionDB,
        request: ToolMockGenerationRequest,
    ) -> str:
        """Construct the user prompt describing the tool and expectations."""

        params_json = json.dumps(tool.parameters or {}, ensure_ascii=False, indent=2)
        example_call = json.dumps(tool.example_call or {}, ensure_ascii=False, indent=2)
        existing_mock = json.dumps(tool.mock_responses or {}, ensure_ascii=False, indent=2)
        scenarios = ToolMockGeneratorService._format_scenarios(request.scenarios)

        preferred_type = request.response_type or "template"
        language_hint = request.language or "zh"
        include_errors = "是" if request.include_error_scenarios else "否"

        instructions = [
            "输出必须是 JSON 对象，不包含额外文本。",
            "字段 enabled 必须为 true。",
            "提供 latency_ms 字段，包含 min 和 max，单位毫秒。",
            f"response_type 优先使用 '{preferred_type}'。",
            "当 response_type 为 template 时，需要提供 response_templates 数组。",
            "每个模板包含 condition 和 response，对应输入条件及返回。",
            "condition 中可以使用 *_default*: true 表示默认场景。",
        ]

        if request.include_error_scenarios:
            instructions.append(
                "提供 error_scenarios 数组，包含 probability、error、error_code 字段。"
            )

        if request.prompt:
            instructions.append(f"额外说明：{request.prompt}")

        prompt_sections = [
            f"请使用 {language_hint} 编写响应字段中的文本描述。",
            f"工具名称: {tool.name}",
            f"工具描述: {tool.description}",
            "参数定义 (JSON Schema):",
            params_json,
        ]

        if tool.example_call:
            prompt_sections.extend(["示例调用:", example_call])

        if tool.mock_responses:
            prompt_sections.extend(["当前 mock 配置(供参考，可改进):", existing_mock])

        if scenarios:
            prompt_sections.extend(["用户提供的场景提示:", scenarios])

        prompt_sections.extend(
            [
                "生成要求:",
                "\n".join(f"- {item}" for item in instructions),
                f"是否需要错误场景: {include_errors}",
                "确保结构可以被 MockToolExecutor 使用。",
            ]
        )

        return "\n".join(section for section in prompt_sections if section).strip()

    @staticmethod
    def _format_scenarios(scenarios: List[MockScenario]) -> str:
        if not scenarios:
            return ""
        formatted = []
        for idx, scenario in enumerate(scenarios, start=1):
            scenario_json = json.dumps(
                {
                    "title": scenario.title,
                    "type": scenario.type,
                    "arguments": scenario.arguments,
                    "expected_behavior": scenario.expected_behavior,
                    "expected_response": scenario.expected_response,
                },
                ensure_ascii=False,
                indent=2,
            )
            formatted.append(f"场景 {idx}:\n{scenario_json}")
        return "\n".join(formatted)

    @staticmethod
    def _extract_json_block(raw_output: str) -> Optional[Dict[str, Any]]:
        """Extract JSON object from LLM output, tolerating code fences."""

        candidates = []
        stripped = raw_output.strip()
        if stripped:
            candidates.append(ToolMockGeneratorService._strip_code_fence(stripped))

        code_fence_match = re.findall(r"```(?:json)?\s*([\s\S]*?)```", raw_output)
        candidates.extend(item.strip() for item in code_fence_match if item.strip())

        for candidate in candidates:
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

        fallback = ToolMockGeneratorService._find_first_json_object(raw_output)
        if fallback:
            try:
                return json.loads(fallback)
            except json.JSONDecodeError:
                logger.debug("Fallback JSON extraction failed", exc_info=True)
        return None

    @staticmethod
    def _strip_code_fence(text: str) -> str:
        if text.startswith("```") and text.endswith("```"):
            inner = text[3:-3]
            inner = inner.lstrip()
            if inner.lower().startswith("json"):
                return inner[4:].strip()
            return inner.strip()
        return text

    @staticmethod
    def _find_first_json_object(text: str) -> Optional[str]:
        """Find the first JSON object using a simple brace stack."""

        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        in_string = False
        escape = False

        for index in range(start, len(text)):
            char = text[index]
            if in_string:
                if escape:
                    escape = False
                elif char == "\\":
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue

            if char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    candidate = text[start : index + 1]
                    return candidate

        return None
