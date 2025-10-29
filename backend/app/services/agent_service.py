"""Agent服务 - 支持完整的工具调用闭环"""
import json
import logging
from typing import Dict, Any, Optional, List, Tuple
from app.models.model_config import ModelConfigDB
from app.services.llm_service import LLMService
from app.services.mock_tool_executor import MockToolExecutor

logger = logging.getLogger(__name__)


class AgentService:
    """Agent服务，支持多轮工具调用和推理"""
    
    @staticmethod
    async def run_agent(
        model_config: ModelConfigDB,
        content: list,
        system_prompt: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tools_config: Optional[Dict[str, Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None,
        use_mock: bool = False,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        运行 Agent，支持多轮工具调用
        
        Args:
            model_config: 模型配置
            content: 用户消息内容
            system_prompt: 系统提示词
            params: 模型参数
            tools: 工具定义列表
            tools_config: 工具配置字典 {tool_name: mock_config}
            conversation_history: 对话历史
            use_mock: 是否使用模拟工具执行
            max_iterations: 最大迭代次数（防止无限循环）
        
        Returns:
            包含最终输出、指标、工具调用历史等信息的字典
        """
        logger.info("=" * 80)
        logger.info("🤖 启动 Agent 运行")
        logger.info(f"模型: {model_config.name}")
        logger.info(f"Mock模式: {use_mock}")
        logger.info(f"最大迭代: {max_iterations}")
        
        # 构建消息历史
        messages = []
        if conversation_history:
            messages.extend(conversation_history)
            logger.info(f"💬 加载对话历史: {len(conversation_history)} 条消息")
        
        # 添加用户消息
        messages.append({
            "role": "user",
            "content": content
        })
        
        # 追踪工具调用历史
        tool_call_history = []
        total_iterations = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0.0
        
        # 迭代执行
        for iteration in range(max_iterations):
            total_iterations += 1
            logger.info(f"\n{'='*80}")
            logger.info(f"🔄 迭代 {iteration + 1}/{max_iterations}")
            
            # 调用模型
            result = await LLMService.call_model(
                model_config=model_config,
                content=messages[-1]["content"] if iteration == 0 else "",
                system_prompt=system_prompt if iteration == 0 else None,
                params=params,
                tools=tools,
                conversation_history=messages[:-1] if iteration == 0 else messages,
                stream=False
            )
            
            # 累计指标
            metrics = result.get("metrics", {})
            total_prompt_tokens += metrics.get("prompt_tokens", 0)
            total_completion_tokens += metrics.get("completion_tokens", 0)
            total_cost += metrics.get("estimated_cost", 0)
            
            # 检查是否有工具调用
            tool_calls = result.get("tool_calls")
            
            if not tool_calls:
                # 没有工具调用，返回最终结果
                logger.info(f"✅ Agent 完成，无需工具调用")
                logger.info(f"📝 最终输出: {result.get('output', '')[:200]}...")
                
                return {
                    "output": result.get("output", ""),
                    "metrics": {
                        "total_iterations": total_iterations,
                        "total_prompt_tokens": total_prompt_tokens,
                        "total_completion_tokens": total_completion_tokens,
                        "total_tokens": total_prompt_tokens + total_completion_tokens,
                        "estimated_cost": total_cost,
                        "response_time": metrics.get("response_time", 0)
                    },
                    "status": result.get("status", "success"),
                    "tool_call_history": tool_call_history,
                    "conversation_history": messages,
                    "error_message": result.get("error_message")
                }
            
            # 有工具调用，记录并执行
            logger.info(f"🔧 检测到 {len(tool_calls)} 个工具调用")
            
            # 将 assistant 消息添加到历史（包含工具调用）
            assistant_message = {
                "role": "assistant",
                "content": result.get("output") or "",
                "tool_calls": tool_calls
            }
            messages.append(assistant_message)
            
            # 执行工具调用
            tool_results = []
            for tool_call in tool_calls:
                function_info = tool_call.get("function", {})
                tool_name = function_info.get("name")
                tool_call_id = tool_call.get("id")
                
                logger.info(f"  🔨 执行工具: {tool_name}")
                
                # 解析参数
                arguments_str = function_info.get("arguments", "{}")
                try:
                    arguments = json.loads(arguments_str) if isinstance(arguments_str, str) else arguments_str
                except json.JSONDecodeError:
                    logger.error(f"❌ 无法解析工具参数: {arguments_str}")
                    arguments = {}
                
                # 执行工具（mock 或真实）
                if use_mock:
                    mock_config = tools_config.get(tool_name) if tools_config else None
                    tool_result = MockToolExecutor.execute_tool_call(
                        tool_name, arguments, mock_config
                    )
                else:
                    # TODO: 实现真实工具执行
                    tool_result = {
                        "success": False,
                        "error": "真实工具执行尚未实现",
                        "note": "请使用 use_mock=True 进行测试"
                    }
                
                logger.info(f"  ✅ 工具执行完成: {json.dumps(tool_result, ensure_ascii=False)[:100]}")
                
                # 记录工具调用历史
                tool_call_record = {
                    "iteration": iteration + 1,
                    "tool_name": tool_name,
                    "arguments": arguments,
                    "result": tool_result,
                    "tool_call_id": tool_call_id
                }
                tool_call_history.append(tool_call_record)
                tool_results.append(tool_call_record)
                
                # 将工具结果添加到消息历史
                tool_message = {
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": json.dumps(tool_result, ensure_ascii=False)
                }
                messages.append(tool_message)
            
            logger.info(f"📦 已添加 {len(tool_results)} 个工具结果到对话历史")
            
            # 如果达到最大迭代次数，终止
            if iteration == max_iterations - 1:
                logger.warning(f"⚠️ 达到最大迭代次数 {max_iterations}，强制终止")
                return {
                    "output": "达到最大工具调用次数，可能未完成全部任务",
                    "metrics": {
                        "total_iterations": total_iterations,
                        "total_prompt_tokens": total_prompt_tokens,
                        "total_completion_tokens": total_completion_tokens,
                        "total_tokens": total_prompt_tokens + total_completion_tokens,
                        "estimated_cost": total_cost,
                        "response_time": metrics.get("response_time", 0)
                    },
                    "status": "max_iterations_reached",
                    "tool_call_history": tool_call_history,
                    "conversation_history": messages,
                    "warning": f"达到最大迭代次数 {max_iterations}"
                }
        
        # 不应该到达这里
        return {
            "output": "",
            "metrics": {},
            "status": "error",
            "error_message": "Agent 执行异常终止"
        }
    
    @staticmethod
    def format_tool_call_history(tool_call_history: List[Dict[str, Any]]) -> str:
        """格式化工具调用历史为可读文本"""
        if not tool_call_history:
            return "无工具调用"
        
        lines = []
        for record in tool_call_history:
            lines.append(f"\n迭代 {record['iteration']}:")
            lines.append(f"  工具: {record['tool_name']}")
            lines.append(f"  参数: {json.dumps(record['arguments'], ensure_ascii=False)}")
            lines.append(f"  结果: {json.dumps(record['result'], ensure_ascii=False)[:100]}...")
        
        return "\n".join(lines)
