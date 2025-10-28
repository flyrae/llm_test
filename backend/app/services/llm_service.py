"""LLM服务层 - 统一的大模型调用接口"""
import time
import asyncio
import logging
import json
from typing import Dict, Any, Optional, AsyncGenerator, List
import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.models.model_config import ModelConfigDB
from app.utils.validators import decrypt_api_key

# 获取日志记录器
logger = logging.getLogger(__name__)


class LLMService:
    """大模型服务"""
    
    @staticmethod
    async def call_model(
        model_config: ModelConfigDB,
        content: list,
        system_prompt: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ):
        """
        调用大模型
        
        Args:
            model_config: 模型配置
            prompt: 用户提示词
            system_prompt: 系统提示词
            params: 模型参数（覆盖默认参数）
            stream: 是否流式输出
            tools: 工具定义列表（用于Function Calling）
            conversation_history: 多轮对话历史 [{"role": "user/assistant", "content": "..."}]
        
        Returns:
            如果stream=True，返回AsyncGenerator
            如果stream=False，返回包含output、metrics的字典
        """
        # 记录请求开始
        logger.info(f"=" * 80)
        logger.info(f"🚀 开始调用大模型")
        logger.info(f"模型配置: {model_config.name} ({model_config.provider}/{model_config.model_name})")
        logger.info(f"系统提示词: {system_prompt[:100] if system_prompt else 'None'}{'...' if system_prompt and len(system_prompt) > 100 else ''}")
        # 如果有对话历史，记录历史轮数
        if conversation_history:
            logger.info(f"💬 对话历史: {len(conversation_history)} 条消息")
        logger.info(f"content: {json.dumps(content, ensure_ascii=False)[:100]}{'...' if len(json.dumps(content, ensure_ascii=False)) > 100 else ''}")
        logger.info(f"参数: {params}")
        logger.info(f"流式模式: {stream}")
        if tools:
            tool_names = [t.get('function', {}).get('name', 'unknown') for t in tools]
            logger.info(f"工具列表: {tool_names}")
        # 合并参数
        model_params = {**(model_config.default_params or {}), **(params or {})}
        # 根据provider调用不同的模型
        if model_config.provider == "openai":
            return await LLMService._call_openai(
                model_config, content, system_prompt, model_params, stream, tools, conversation_history
            )
        elif model_config.provider == "anthropic":
            return await LLMService._call_anthropic(
                model_config, content, system_prompt, model_params, stream, tools
            )
        elif model_config.provider == "local":
            return await LLMService._call_local(
                model_config, content, system_prompt, model_params, stream, tools
            )
        elif model_config.provider == "custom":
            return await LLMService._call_custom(
                model_config, content, system_prompt, model_params, stream, tools, conversation_history
            )
        else:
            raise ValueError(f"Unsupported provider: {model_config.provider}")
    
    @staticmethod
    async def _call_openai(
        model_config: ModelConfigDB,
        content: list,
        system_prompt: Optional[str],
        params: Dict[str, Any],
        stream: bool,
        tools: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """调用OpenAI API"""
        logger.info(f"📡 调用 OpenAI API: {model_config.api_endpoint or 'https://api.openai.com'}")
        
        api_key = decrypt_api_key(model_config.api_key) if model_config.api_key else None
        base_url = model_config.api_endpoint or None
        
        client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        
        # 构建消息列表
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        if conversation_history:
            messages.extend(conversation_history)
            logger.info(f"💬 添加 {len(conversation_history)} 条历史消息")
        # 直接用content数组
        messages.append({"role": "user", "content": content})
        
        start_time = time.time()
        
        try:
            # 准备请求参数
            request_params = {
                "model": model_config.model_name,
                "messages": messages,
                "temperature": params.get("temperature", 0.7),
                "top_p": params.get("top_p", 1.0),
                "max_tokens": params.get("max_tokens", 1000),
                "frequency_penalty": params.get("frequency_penalty", 0),
                "presence_penalty": params.get("presence_penalty", 0),
                "stream": stream
            }
            
            # 如果提供了工具定义，添加到请求中
            if tools:
                request_params["tools"] = tools
                request_params["tool_choice"] = "auto"
                logger.info(f"🔧 包含 {len(tools)} 个工具定义")
            
            # 记录请求参数（排除messages内容以避免日志过长）
            log_params = {k: v for k, v in request_params.items() if k != "messages"}
            log_params["messages"] = [{"role": msg["role"], "content": f"{msg['content'][:50]}..."} for msg in request_params["messages"]]
            logger.info(f"📤 发送请求参数: {json.dumps(log_params, ensure_ascii=False, indent=2)}")
            
            # 如果是流式模式，返回异步生成器
            if stream:
                return LLMService._stream_openai_response(
                    client, request_params, start_time, model_config
                )
            
            # 非流式模式
            response = await client.chat.completions.create(**request_params)
            
            # 计算响应时间
            response_time = time.time() - start_time
            
            # 获取响应消息
            message = response.choices[0].message
            output = message.content or ""
            logger.info(f"🔧 模型返回：{message}")
            
            # 检查是否有工具调用
            tool_calls_info = None
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tool_calls_info = []
                for tool_call in message.tool_calls:
                    tool_calls_info.append({
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    })
                logger.info(f"🔧 模型请求调用 {len(tool_calls_info)} 个工具:")
                for tc in tool_calls_info:
                    logger.info(f"   - {tc['function']['name']}: {tc['function']['arguments'][:100]}")
                
                # 如果有工具调用但没有文本输出，生成简短说明（不包含详细信息）
                if not output:
                    output = f""
                    logger.info(f"📝 设置输出提示: {output}")
            
            # 构建指标
            metrics = {
                "response_time": response_time,
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
                "estimated_cost": LLMService._estimate_openai_cost(
                    model_config.model_name,
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
            }
            
            logger.info(f"✅ OpenAI 调用成功")
            logger.info(f"📊 响应时间: {response_time:.2f}s")
            logger.info(f"📊 Tokens: {metrics['prompt_tokens']} + {metrics['completion_tokens']} = {metrics['total_tokens']}")
            logger.info(f"💰 估算成本: ${metrics['estimated_cost']:.6f}")
            logger.info(f"📝 输出预览: {output[:200]}{'...' if len(output) > 200 else ''}")
            
            result = {
                "output": output,
                "metrics": metrics,
                "status": "success"
            }
            
            # 如果有工具调用，添加到结果中
            if tool_calls_info:
                result["tool_calls"] = tool_calls_info
            
            return result
            
        except Exception as e:
            logger.error(f"❌ OpenAI 调用失败: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            return {
                "output": "",
                "metrics": {"response_time": time.time() - start_time},
                "status": "error",
                "error_message": str(e)
            }
    
    @staticmethod
    async def _stream_openai_response(
        client: AsyncOpenAI,
        request_params: Dict[str, Any],
        start_time: float,
        model_config: ModelConfigDB
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        处理OpenAI流式响应
        
        Yields:
            包含流式数据块的字典
        """
        logger.info(f"🔄 开始流式输出")
        
        full_content = ""
        tool_calls_info = []
        prompt_tokens = 0
        completion_tokens = 0
        total_chunks = 0
        
        try:
            stream = await client.chat.completions.create(**request_params)
            
            async for chunk in stream:
                total_chunks += 1
                
                # 安全地访问 choices
                if not chunk.choices or len(chunk.choices) == 0:
                    continue
                
                delta = chunk.choices[0].delta
                
                # 处理文本内容
                if hasattr(delta, 'content') and delta.content:
                    full_content += delta.content
                    yield {
                        "content": delta.content,
                        "done": False
                    }
                
                # 处理工具调用
                if hasattr(delta, 'tool_calls') and delta.tool_calls:
                    for tool_call in delta.tool_calls:
                        if hasattr(tool_call, 'function') and tool_call.function:
                            yield {
                                "tool_call": {
                                    "id": getattr(tool_call, 'id', None),
                                    "name": tool_call.function.name,
                                    "arguments": tool_call.function.arguments
                                },
                                "done": False
                            }
                
                # 处理usage信息（通常在最后一个chunk）
                # 注意：不是所有API都会在流式模式返回usage
                if hasattr(chunk, 'usage') and chunk.usage:
                    usage = chunk.usage
                    if hasattr(usage, 'prompt_tokens'):
                        prompt_tokens = usage.prompt_tokens
                    if hasattr(usage, 'completion_tokens'):
                        completion_tokens = usage.completion_tokens
            
            response_time = time.time() - start_time
            
            # 如果没有获取到token信息，进行估算
            if prompt_tokens == 0:
                # 粗略估算：英文约4字符=1token，中文约1.5字符=1token
                # 这里简单按2字符=1token估算
                prompt_tokens = len(request_params.get("messages", [{}])[0].get("content", "")) // 2
            if completion_tokens == 0:
                completion_tokens = len(full_content) // 2
            
            # 构建最终响应
            metrics = {
                "response_time": response_time,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
                "estimated_cost": LLMService._estimate_openai_cost(
                    model_config.model_name,
                    prompt_tokens,
                    completion_tokens
                )
            }
            
            final_response = {
                "output": full_content,
                "metrics": metrics,
                "status": "success"
            }
            
            if tool_calls_info:
                final_response["tool_calls"] = tool_calls_info
            
            # 发送完成信号
            yield {
                "done": True,
                "final_response": final_response,
                "metrics": metrics
            }
            
            logger.info(f"✅ 流式输出完成")
            logger.info(f"📊 响应时间: {response_time:.2f}s")
            logger.info(f"📊 总块数: {total_chunks}")
            logger.info(f"📊 Tokens: {prompt_tokens} + {completion_tokens} = {prompt_tokens + completion_tokens}")
            logger.info(f"📝 完整输出长度: {len(full_content)} 字符")
            
        except Exception as e:
            logger.error(f"❌ 流式输出失败: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            import traceback
            logger.error(f"堆栈跟踪: {traceback.format_exc()}")
            yield {
                "done": True,
                "error": str(e),
                "status": "error"
            }
    
    @staticmethod
    async def _call_anthropic(
        model_config: ModelConfigDB,
        content: list,
        system_prompt: Optional[str],
        params: Dict[str, Any],
        stream: bool,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """调用Anthropic Claude API"""
        logger.info(f"📡 调用 Anthropic API")
        
        api_key = decrypt_api_key(model_config.api_key) if model_config.api_key else None
        
        client = AsyncAnthropic(api_key=api_key)
        
        start_time = time.time()
        
        try:
            if tools:
                logger.info(f"🔧 包含 {len(tools)} 个工具定义")
                
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": content})
            response = await client.messages.create(
                model=model_config.model_name,
                max_tokens=params.get("max_tokens", 1000),
                temperature=params.get("temperature", 0.7),
                system=system_prompt or "",
                messages=messages
            )
            
            response_time = time.time() - start_time
            output = response.content[0].text
            
            metrics = {
                "response_time": response_time,
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                "estimated_cost": LLMService._estimate_anthropic_cost(
                    model_config.model_name,
                    response.usage.input_tokens,
                    response.usage.output_tokens
                )
            }
            
            logger.info(f"✅ Anthropic 调用成功")
            logger.info(f"📊 响应时间: {response_time:.2f}s")
            logger.info(f"📊 Tokens: {metrics['prompt_tokens']} + {metrics['completion_tokens']} = {metrics['total_tokens']}")
            logger.info(f"💰 估算成本: ${metrics['estimated_cost']:.6f}")
            logger.info(f"📝 输出预览: {output[:200]}{'...' if len(output) > 200 else ''}")
            
            return {
                "output": output,
                "metrics": metrics,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Anthropic 调用失败: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            return {
                "output": "",
                "metrics": {"response_time": time.time() - start_time},
                "status": "error",
                "error_message": str(e)
            }
    
    @staticmethod
    async def _call_local(
        model_config: ModelConfigDB,
        content: list,
        system_prompt: Optional[str],
        params: Dict[str, Any],
        stream: bool,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """调用本地模型（Ollama等）"""
        endpoint = model_config.api_endpoint or "http://localhost:11434"
        logger.info(f"📡 调用本地模型: {endpoint}")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": content})
        
        start_time = time.time()
        
        try:
            if tools:
                logger.info(f"🔧 包含 {len(tools)} 个工具定义 (本地模型可能不支持)")
                
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{endpoint}/api/chat",
                    json={
                        "model": model_config.model_name,
                        "messages": messages,
                        "stream": False,
                        "options": {
                            "temperature": params.get("temperature", 0.7),
                            "top_p": params.get("top_p", 1.0),
                        }
                    },
                    timeout=120.0
                )
                
                response_time = time.time() - start_time
                result = response.json()
                output = result.get("message", {}).get("content", "")
                
                metrics = {
                    "response_time": response_time,
                    "prompt_tokens": 0,  # Ollama不提供token计数
                    "completion_tokens": 0,
                    "total_tokens": 0,
                    "estimated_cost": 0.0
                }
                
                logger.info(f"✅ 本地模型调用成功")
                logger.info(f"📊 响应时间: {response_time:.2f}s")
                logger.info(f"📝 输出预览: {output[:200]}{'...' if len(output) > 200 else ''}")
                
                return {
                    "output": output,
                    "metrics": metrics,
                    "status": "success"
                }
                
        except Exception as e:
            logger.error(f"❌ 本地模型调用失败: {str(e)}")
            logger.error(f"错误类型: {type(e).__name__}")
            return {
                "output": "",
                "metrics": {"response_time": time.time() - start_time},
                "status": "error",
                "error_message": str(e)
            }
    
    @staticmethod
    async def _call_custom(
        model_config: ModelConfigDB,
        content: list,
        system_prompt: Optional[str],
        params: Dict[str, Any],
        stream: bool,
        tools: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """调用自定义API"""
        # 自定义API的通用实现
        return await LLMService._call_openai(
            model_config, content, system_prompt, params, stream, tools, conversation_history
        )
    
    @staticmethod
    def _estimate_openai_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        """估算OpenAI API成本（USD）"""
        # 简化的价格表（2024年价格）
        prices = {
            "gpt-4": (0.03, 0.06),
            "gpt-4-turbo": (0.01, 0.03),
            "gpt-3.5-turbo": (0.0005, 0.0015),
        }
        
        for key, (input_price, output_price) in prices.items():
            if key in model_name.lower():
                return (prompt_tokens / 1000 * input_price) + (completion_tokens / 1000 * output_price)
        
        return 0.0
    
    @staticmethod
    def _estimate_anthropic_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
        """估算Anthropic API成本（USD）"""
        prices = {
            "claude-3-opus": (0.015, 0.075),
            "claude-3-sonnet": (0.003, 0.015),
            "claude-3-haiku": (0.00025, 0.00125),
        }
        
        for key, (input_price, output_price) in prices.items():
            if key in model_name.lower():
                return (input_tokens / 1000 * input_price) + (output_tokens / 1000 * output_price)
        
        return 0.0
