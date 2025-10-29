"""Mock工具执行器 - 用于Agent训练的模拟工具调用"""
import json
import random
import time
import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class MockToolExecutor:
    """模拟工具执行器"""
    
    # Mock配置预设模板
    PRESET_TEMPLATES = {
        "simple_success": {
            "enabled": True,
            "response_type": "static",
            "static_response": {
                "success": True,
                "message": "操作成功",
                "data": {}
            },
            "latency_ms": {"min": 100, "max": 300}
        },
        "simple_error": {
            "enabled": True,
            "response_type": "static",
            "static_response": {
                "success": False,
                "error": "操作失败",
                "error_code": "ERROR"
            },
            "latency_ms": {"min": 100, "max": 300}
        },
        "api_simulation": {
            "enabled": True,
            "response_type": "template",
            "response_templates": [
                {
                    "condition": {"_default": True},
                    "response": {
                        "success": True,
                        "data": {
                            "result": "{{args.query}}的结果",
                            "timestamp": "{{timestamp}}"
                        }
                    }
                }
            ],
            "latency_ms": {"min": 200, "max": 800}
        }
    }
    
    @staticmethod
    def validate_mock_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证 mock 配置的合法性
        
        Returns:
            (is_valid, error_message)
        """
        if config is None:
            return True, None
        
        if not isinstance(config, dict):
            return False, "配置必须是字典格式"
        
        # 如果未启用，跳过验证
        if not config.get("enabled", False):
            return True, None
        
        # 验证响应类型
        response_type = config.get("response_type")
        if response_type not in ["static", "template", "dynamic"]:
            return False, f"不支持的响应类型: {response_type}，必须是 static, template 或 dynamic"
        
        # 验证静态响应
        if response_type == "static":
            if "static_response" not in config:
                return False, "static 类型必须包含 static_response 字段"
        
        # 验证模板响应
        if response_type == "template":
            if "response_templates" not in config:
                return False, "template 类型必须包含 response_templates 字段"
            
            templates = config.get("response_templates")
            if not isinstance(templates, list) or len(templates) == 0:
                return False, "response_templates 必须是非空数组"
            
            for idx, template in enumerate(templates):
                if not isinstance(template, dict):
                    return False, f"第 {idx+1} 个模板必须是对象"
                if "response" not in template:
                    return False, f"第 {idx+1} 个模板缺少 response 字段"
        
        # 验证动态响应
        if response_type == "dynamic":
            if "dynamic_rules" not in config:
                return False, "dynamic 类型必须包含 dynamic_rules 字段"
        
        # 验证延迟配置
        if "latency_ms" in config:
            latency = config["latency_ms"]
            if not isinstance(latency, dict):
                return False, "latency_ms 必须是对象"
            if "min" in latency and "max" in latency:
                if not isinstance(latency["min"], (int, float)) or not isinstance(latency["max"], (int, float)):
                    return False, "latency_ms 的 min 和 max 必须是数字"
                if latency["min"] > latency["max"]:
                    return False, "latency_ms 的 min 不能大于 max"
        
        return True, None
    
    @staticmethod
    def get_preset_template(name: str) -> Optional[Dict[str, Any]]:
        """获取预设模板"""
        return MockToolExecutor.PRESET_TEMPLATES.get(name)
    
    @staticmethod
    def list_preset_templates() -> List[Dict[str, Any]]:
        """列出所有预设模板"""
        return [
            {
                "name": name,
                "description": MockToolExecutor._get_template_description(name),
                "template": template
            }
            for name, template in MockToolExecutor.PRESET_TEMPLATES.items()
        ]
    
    @staticmethod
    def _get_template_description(name: str) -> str:
        """获取模板描述"""
        descriptions = {
            "simple_success": "简单成功响应 - 返回固定的成功消息",
            "simple_error": "简单错误响应 - 返回固定的错误消息",
            "api_simulation": "API模拟 - 根据参数返回动态响应"
        }
        return descriptions.get(name, "")
    
    @staticmethod
    def execute_tool_call(
        tool_name: str,
        tool_arguments: Dict[str, Any],
        mock_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        执行模拟工具调用
        
        Args:
            tool_name: 工具名称
            tool_arguments: 工具调用参数
            mock_config: 模拟配置
        
        Returns:
            模拟的工具执行结果
        """
        logger.info(f"🎭 执行模拟工具调用: {tool_name}")
        logger.info(f"📥 参数: {json.dumps(tool_arguments, ensure_ascii=False)}")
        
        # 如果没有配置，返回默认响应
        if not mock_config or not mock_config.get("enabled", False):
            logger.warning(f"⚠️ 工具 {tool_name} 未启用 mock 配置，返回默认响应")
            return MockToolExecutor._default_response(tool_name, tool_arguments)
        
        # 模拟延迟
        latency_config = mock_config.get("latency_ms", {})
        latency = random.randint(
            latency_config.get("min", 100),
            latency_config.get("max", 500)
        )
        time.sleep(latency / 1000.0)
        
        # 检查错误场景
        error_scenarios = mock_config.get("error_scenarios", [])
        for error_scenario in error_scenarios:
            if random.random() < error_scenario.get("probability", 0):
                logger.warning(f"🔥 触发错误场景: {error_scenario.get('error')}")
                return {
                    "success": False,
                    "error": error_scenario.get("error"),
                    "error_code": error_scenario.get("error_code", "MOCK_ERROR"),
                    "tool_name": tool_name,
                    "timestamp": datetime.now().isoformat()
                }
        
        # 根据响应类型生成响应
        response_type = mock_config.get("response_type", "static")
        
        if response_type == "static":
            response = MockToolExecutor._static_response(mock_config, tool_name, tool_arguments)
        elif response_type == "template":
            response = MockToolExecutor._template_response(mock_config, tool_name, tool_arguments)
        elif response_type == "dynamic":
            response = MockToolExecutor._dynamic_response(mock_config, tool_name, tool_arguments)
        else:
            response = MockToolExecutor._default_response(tool_name, tool_arguments)
        
        logger.info(f"✅ 模拟执行完成，耗时: {latency}ms")
        logger.info(f"📤 响应: {json.dumps(response, ensure_ascii=False)[:200]}")
        
        return response
    
    @staticmethod
    def _default_response(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """默认响应"""
        return {
            "success": True,
            "tool_name": tool_name,
            "message": f"工具 {tool_name} 模拟执行成功",
            "data": {
                "input_arguments": arguments,
                "note": "这是默认的模拟响应，请配置 mock_responses 以自定义响应"
            },
            "timestamp": datetime.now().isoformat()
        }
    
    @staticmethod
    def _static_response(
        mock_config: Dict[str, Any],
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """静态响应 - 返回预定义的固定响应"""
        static_response = mock_config.get("static_response", {})
        
        # 添加元数据
        response = {
            **static_response,
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat(),
            "_mock_mode": "static"
        }
        
        return response
    
    @staticmethod
    def _template_response(
        mock_config: Dict[str, Any],
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """模板响应 - 根据条件匹配和模板生成响应"""
        response_templates = mock_config.get("response_templates", [])
        
        # 查找匹配的模板
        matched_template = None
        for template in response_templates:
            condition = template.get("condition", {})
            if MockToolExecutor._match_condition(condition, arguments):
                matched_template = template
                break
        
        # 如果没有匹配，使用默认模板
        if not matched_template:
            for template in response_templates:
                if template.get("condition", {}).get("_default", False):
                    matched_template = template
                    break
        
        if not matched_template:
            logger.warning(f"⚠️ 未找到匹配的模板，返回默认响应")
            return MockToolExecutor._default_response(tool_name, arguments)
        
        # 渲染模板
        response_template = matched_template.get("response", {})
        rendered_response = MockToolExecutor._render_template(response_template, arguments)
        
        # 添加元数据
        rendered_response.update({
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat(),
            "_mock_mode": "template"
        })
        
        return rendered_response
    
    @staticmethod
    def _dynamic_response(
        mock_config: Dict[str, Any],
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """动态响应 - 基于自定义逻辑生成响应"""
        # 这里可以扩展更复杂的动态逻辑
        # 目前简化为基于参数的动态生成
        
        dynamic_rules = mock_config.get("dynamic_rules", {})
        response = {
            "success": True,
            "tool_name": tool_name,
            "timestamp": datetime.now().isoformat(),
            "_mock_mode": "dynamic"
        }
        
        # 应用动态规则
        for key, rule in dynamic_rules.items():
            response[key] = MockToolExecutor._apply_rule(rule, arguments)
        
        return response
    
    @staticmethod
    def _match_condition(condition: Dict[str, Any], arguments: Dict[str, Any]) -> bool:
        """检查参数是否匹配条件"""
        for key, expected_value in condition.items():
            if key.startswith("_"):  # 跳过特殊键
                continue
            
            if key not in arguments:
                return False
            
            actual_value = arguments[key]
            
            # 支持通配符 *
            if expected_value == "*":
                continue
            
            # 支持正则表达式
            if isinstance(expected_value, str) and expected_value.startswith("regex:"):
                pattern = expected_value[6:]
                if not re.match(pattern, str(actual_value)):
                    return False
            # 精确匹配
            elif actual_value != expected_value:
                return False
        
        return True
    
    @staticmethod
    def _render_template(template: Any, arguments: Dict[str, Any]) -> Any:
        """渲染模板，支持变量替换和函数调用"""
        if isinstance(template, dict):
            return {k: MockToolExecutor._render_template(v, arguments) for k, v in template.items()}
        elif isinstance(template, list):
            return [MockToolExecutor._render_template(item, arguments) for item in template]
        elif isinstance(template, str):
            # 支持 {{variable}} 语法
            def replace_var(match):
                var_expr = match.group(1).strip()
                return str(MockToolExecutor._evaluate_expression(var_expr, arguments))
            
            return re.sub(r'\{\{(.+?)\}\}', replace_var, template)
        else:
            return template
    
    @staticmethod
    def _evaluate_expression(expression: str, arguments: Dict[str, Any]) -> Any:
        """评估表达式"""
        # 支持 random(min, max)
        if expression.startswith("random(") and expression.endswith(")"):
            args = expression[7:-1].split(",")
            if len(args) == 2:
                try:
                    min_val = int(args[0].strip())
                    max_val = int(args[1].strip())
                    return random.randint(min_val, max_val)
                except ValueError:
                    pass
        
        # 支持 random([item1, item2, ...])
        if expression.startswith("random([") and expression.endswith("])"):
            items_str = expression[8:-2]
            items = [item.strip().strip("'\"") for item in items_str.split(",")]
            return random.choice(items)
        
        # 支持参数引用 args.param_name
        if expression.startswith("args."):
            param_name = expression[5:]
            return arguments.get(param_name, f"{{missing: {param_name}}}")
        
        # 支持时间戳
        if expression == "timestamp":
            return datetime.now().isoformat()
        
        # 默认返回表达式本身
        return expression
    
    @staticmethod
    def _apply_rule(rule: Any, arguments: Dict[str, Any]) -> Any:
        """应用动态规则"""
        if isinstance(rule, str):
            return MockToolExecutor._evaluate_expression(rule, arguments)
        elif isinstance(rule, dict) and "type" in rule:
            rule_type = rule["type"]
            if rule_type == "random_int":
                return random.randint(rule.get("min", 0), rule.get("max", 100))
            elif rule_type == "random_choice":
                return random.choice(rule.get("choices", []))
            elif rule_type == "argument":
                return arguments.get(rule.get("key"), rule.get("default"))
        
        return rule
    
    @staticmethod
    def execute_multiple_tool_calls(
        tool_calls: List[Dict[str, Any]],
        tools_config: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        执行多个工具调用
        
        Args:
            tool_calls: 工具调用列表 [{"function": {"name": "...", "arguments": "..."}}]
            tools_config: 工具配置字典 {tool_name: mock_config}
        
        Returns:
            工具执行结果列表
        """
        results = []
        
        for tool_call in tool_calls:
            function_info = tool_call.get("function", {})
            tool_name = function_info.get("name")
            
            # 解析参数
            arguments_str = function_info.get("arguments", "{}")
            try:
                arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
            except json.JSONDecodeError:
                logger.error(f"❌ 无法解析工具参数: {arguments_str}")
                arguments = {}
            
            # 获取工具配置
            mock_config = tools_config.get(tool_name)
            
            # 执行工具调用
            result = MockToolExecutor.execute_tool_call(tool_name, arguments, mock_config)
            
            results.append({
                "tool_call_id": tool_call.get("id"),
                "tool_name": tool_name,
                "result": result
            })
        
        return results
