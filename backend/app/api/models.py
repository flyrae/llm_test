"""模型配置管理API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel
import httpx
import asyncio

from app.utils.database import get_db
from app.models.model_config import (
    ModelConfigDB, ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse
)
from app.utils.validators import validate_api_endpoint, encrypt_api_key

router = APIRouter()


# 预设配置
PROVIDER_PRESETS = {
    "openai": {
        "name": "OpenAI",
        "endpoint": "https://api.openai.com/v1/chat/completions",
        "models": [
            {"name": "gpt-4", "display": "GPT-4", "desc": "最强大的GPT-4模型"},
            {"name": "gpt-4-turbo", "display": "GPT-4 Turbo", "desc": "GPT-4的优化版本"},
            {"name": "gpt-4o", "display": "GPT-4o", "desc": "多模态版本的GPT-4"},
            {"name": "gpt-3.5-turbo", "display": "GPT-3.5 Turbo", "desc": "经济高效的选择"},
            {"name": "gpt-3.5-turbo-16k", "display": "GPT-3.5 Turbo 16K", "desc": "支持更长上下文"}
        ]
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "endpoint": "https://api.anthropic.com/v1/messages",
        "models": [
            {"name": "claude-3-opus-20240229", "display": "Claude 3 Opus", "desc": "最强大的Claude模型"},
            {"name": "claude-3-sonnet-20240229", "display": "Claude 3 Sonnet", "desc": "平衡性能和成本"},
            {"name": "claude-3-haiku-20240307", "display": "Claude 3 Haiku", "desc": "最快最经济"},
            {"name": "claude-2.1", "display": "Claude 2.1", "desc": "上一代Claude模型"}
        ]
    },
    "gemini": {
        "name": "Google Gemini",
        "endpoint": "https://generativelanguage.googleapis.com/v1beta/models/",
        "models": [
            {"name": "gemini-pro", "display": "Gemini Pro", "desc": "Google最强大的文本模型"},
            {"name": "gemini-pro-vision", "display": "Gemini Pro Vision", "desc": "支持图像理解的多模态模型"},
            {"name": "gemini-1.5-pro", "display": "Gemini 1.5 Pro", "desc": "最新版本的Gemini Pro"},
            {"name": "gemini-1.5-flash", "display": "Gemini 1.5 Flash", "desc": "更快的轻量级版本"}
        ]
    },
    "azure_openai": {
        "name": "Azure OpenAI",
        "endpoint": "https://{resource}.openai.azure.com/openai/deployments/{deployment}/chat/completions",
        "models": [
            {"name": "gpt-4", "display": "GPT-4", "desc": "Azure部署的GPT-4"},
            {"name": "gpt-4-turbo", "display": "GPT-4 Turbo", "desc": "Azure部署的GPT-4 Turbo"},
            {"name": "gpt-35-turbo", "display": "GPT-3.5 Turbo", "desc": "Azure部署的GPT-3.5"},
            {"name": "gpt-35-turbo-16k", "display": "GPT-3.5 Turbo 16K", "desc": "Azure部署的GPT-3.5 16K"}
        ]
    },
    "together": {
        "name": "Together AI",
        "endpoint": "https://api.together.xyz/v1/chat/completions",
        "models": [
            {"name": "meta-llama/Llama-2-70b-chat-hf", "display": "Llama 2 70B Chat", "desc": "Meta Llama 2 70B聊天模型"},
            {"name": "meta-llama/Llama-2-13b-chat-hf", "display": "Llama 2 13B Chat", "desc": "Meta Llama 2 13B聊天模型"},
            {"name": "meta-llama/Llama-2-7b-chat-hf", "display": "Llama 2 7B Chat", "desc": "Meta Llama 2 7B聊天模型"},
            {"name": "mistralai/Mixtral-8x7B-Instruct-v0.1", "display": "Mixtral 8x7B", "desc": "Mistral的混合专家模型"},
            {"name": "togethercomputer/RedPajama-INCITE-Chat-3B-v1", "display": "RedPajama Chat 3B", "desc": "轻量级聊天模型"}
        ]
    },
    "huggingface": {
        "name": "Hugging Face Inference",
        "endpoint": "https://api-inference.huggingface.co/models/",
        "models": [
            {"name": "microsoft/DialoGPT-large", "display": "DialoGPT Large", "desc": "微软的对话模型"},
            {"name": "facebook/blenderbot-400M-distill", "display": "BlenderBot 400M", "desc": "Facebook的聊天机器人"},
            {"name": "microsoft/GODEL-v1_1-large-seq2seq", "display": "GODEL Large", "desc": "微软的目标导向对话模型"},
            {"name": "EleutherAI/gpt-j-6b", "display": "GPT-J 6B", "desc": "EleutherAI的开源GPT模型"}
        ]
    },
    "cohere": {
        "name": "Cohere",
        "endpoint": "https://api.cohere.ai/v1/chat",
        "models": [
            {"name": "command", "display": "Command", "desc": "Cohere的指令遵循模型"},
            {"name": "command-light", "display": "Command Light", "desc": "轻量级的Command模型"},
            {"name": "command-nightly", "display": "Command Nightly", "desc": "最新的实验性Command模型"},
            {"name": "command-r", "display": "Command R", "desc": "Cohere的检索增强模型"}
        ]
    },
    "deepseek": {
        "name": "DeepSeek",
        "endpoint": "https://api.deepseek.com/v1/chat/completions",
        "models": [
            {"name": "deepseek-chat", "display": "DeepSeek Chat", "desc": "DeepSeek的聊天模型"},
            {"name": "deepseek-coder", "display": "DeepSeek Coder", "desc": "专门的代码生成模型"},
            {"name": "deepseek-math", "display": "DeepSeek Math", "desc": "数学专用模型"}
        ]
    },
    "zhipu": {
        "name": "智谱AI (GLM)",
        "endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
        "models": [
            {"name": "glm-4", "display": "GLM-4", "desc": "智谱AI最新的大模型"},
            {"name": "glm-4-air", "display": "GLM-4 Air", "desc": "轻量化版本"},
            {"name": "glm-3-turbo", "display": "GLM-3 Turbo", "desc": "高性价比版本"},
            {"name": "chatglm3-6b", "display": "ChatGLM3-6B", "desc": "开源版本"}
        ]
    },
    "moonshot": {
        "name": "月之暗面 (Kimi)",
        "endpoint": "https://api.moonshot.cn/v1/chat/completions",
        "models": [
            {"name": "moonshot-v1-8k", "display": "Moonshot v1 8K", "desc": "支持8K上下文"},
            {"name": "moonshot-v1-32k", "display": "Moonshot v1 32K", "desc": "支持32K上下文"},
            {"name": "moonshot-v1-128k", "display": "Moonshot v1 128K", "desc": "支持128K长上下文"}
        ]
    },
    "baichuan": {
        "name": "百川智能",
        "endpoint": "https://api.baichuan-ai.com/v1/chat/completions",
        "models": [
            {"name": "Baichuan2-Turbo", "display": "百川2 Turbo", "desc": "百川智能的高性能模型"},
            {"name": "Baichuan2-Turbo-192k", "display": "百川2 Turbo 192K", "desc": "支持超长上下文"},
            {"name": "Baichuan-Text-Embedding", "display": "百川文本嵌入", "desc": "文本向量化模型"}
        ]
    },
    "doubao": {
        "name": "字节跳动 (豆包)",
        "endpoint": "https://ark.cn-beijing.volces.com/api/v3/chat/completions",
        "models": [
            {"name": "ep-20231002173720-lmxvs", "display": "豆包 Pro", "desc": "字节跳动的大模型"},
            {"name": "ep-20231002173720-xxxxx", "display": "豆包 Lite", "desc": "轻量版本"}
        ]
    },
    "minimax": {
        "name": "MiniMax",
        "endpoint": "https://api.minimax.chat/v1/text/chatcompletion_pro",
        "models": [
            {"name": "abab6-chat", "display": "ABAB 6 Chat", "desc": "MiniMax的聊天模型"},
            {"name": "abab5.5-chat", "display": "ABAB 5.5 Chat", "desc": "上一代聊天模型"},
            {"name": "abab6-embedding", "display": "ABAB 6 Embedding", "desc": "文本嵌入模型"}
        ]
    },
    "local": {
        "name": "本地模型 (Ollama)",
        "endpoint": "http://localhost:11434/api/chat",
        "models": [
            {"name": "llama2", "display": "Llama 2", "desc": "Meta的开源大语言模型"},
            {"name": "llama2:13b", "display": "Llama 2 13B", "desc": "Llama 2 13B参数版本"},
            {"name": "llama2:70b", "display": "Llama 2 70B", "desc": "Llama 2 70B参数版本"},
            {"name": "codellama", "display": "Code Llama", "desc": "专门用于代码生成"},
            {"name": "codellama:13b", "display": "Code Llama 13B", "desc": "Code Llama 13B版本"},
            {"name": "mistral", "display": "Mistral 7B", "desc": "高效的开源模型"},
            {"name": "mistral:instruct", "display": "Mistral Instruct", "desc": "指令调优版本"},
            {"name": "qwen", "display": "Qwen", "desc": "阿里巴巴通义千问"},
            {"name": "qwen:14b", "display": "Qwen 14B", "desc": "通义千问14B版本"},
            {"name": "chatglm3", "display": "ChatGLM3", "desc": "智谱AI开源模型"},
            {"name": "baichuan2", "display": "Baichuan2", "desc": "百川智能开源模型"},
            {"name": "deepseek-coder", "display": "DeepSeek Coder", "desc": "DeepSeek代码模型"},
            {"name": "phi", "display": "Phi", "desc": "微软的小型模型"},
            {"name": "gemma", "display": "Gemma", "desc": "Google的开源模型"},
            {"name": "yi", "display": "Yi", "desc": "零一万物开源模型"}
        ]
    },
    "custom": {
        "name": "自定义端点",
        "endpoint": "",
        "models": [
            {"name": "custom-model-1", "display": "自定义模型 1", "desc": "自定义模型配置"},
            {"name": "custom-model-2", "display": "自定义模型 2", "desc": "自定义模型配置"}
        ]
    }
}


class QuickSetupRequest(BaseModel):
    """快速设置请求"""
    provider: str  # openai, anthropic, local
    api_key: str = ""  # API密钥（本地模型可为空）
    endpoint: str = ""  # 自定义端点（可选）
    selected_models: List[str] = []  # 选择的模型，空表示全部


class FetchModelsRequest(BaseModel):
    """获取端点模型列表请求"""
    api_endpoint: str
    api_key: str = ""
    provider: str = "custom"  # 用于确定请求格式


@router.get("/", response_model=List[ModelConfigResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取模型列表"""
    models = db.query(ModelConfigDB).offset(skip).limit(limit).all()
    return models


@router.get("/{model_id}", response_model=ModelConfigResponse)
async def get_model(model_id: int, db: Session = Depends(get_db)):
    """获取单个模型配置"""
    model = db.query(ModelConfigDB).filter(ModelConfigDB.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/", response_model=ModelConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_config: ModelConfigCreate,
    db: Session = Depends(get_db)
):
    """创建模型配置"""
    # 验证API端点
    if model_config.api_endpoint and not validate_api_endpoint(model_config.api_endpoint):
        raise HTTPException(status_code=400, detail="Invalid API endpoint")
    
    # 检查名称是否已存在
    existing = db.query(ModelConfigDB).filter(ModelConfigDB.name == model_config.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model name already exists")
    
    # 加密API密钥
    encrypted_key = None
    if model_config.api_key:
        encrypted_key = encrypt_api_key(model_config.api_key)
    
    # 创建数据库记录
    db_model = ModelConfigDB(
        name=model_config.name,
        provider=model_config.provider,
        api_endpoint=model_config.api_endpoint,
        api_key=encrypted_key,
        model_name=model_config.model_name,
        default_params=model_config.default_params or {},
        tags=model_config.tags,
        description=model_config.description
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.put("/{model_id}", response_model=ModelConfigResponse)
async def update_model(
    model_id: int,
    model_config: ModelConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新模型配置"""
    db_model = db.query(ModelConfigDB).filter(ModelConfigDB.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # 更新字段
    update_data = model_config.model_dump(exclude_unset=True)
    
    # 验证API端点
    if "api_endpoint" in update_data and update_data["api_endpoint"]:
        if not validate_api_endpoint(update_data["api_endpoint"]):
            raise HTTPException(status_code=400, detail="Invalid API endpoint")
    
    # 加密API密钥
    if "api_key" in update_data and update_data["api_key"]:
        update_data["api_key"] = encrypt_api_key(update_data["api_key"])
    
    # default_params已经是字典，不需要额外处理
    
    for key, value in update_data.items():
        setattr(db_model, key, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: int, db: Session = Depends(get_db)):
    """删除模型配置"""
    db_model = db.query(ModelConfigDB).filter(ModelConfigDB.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(db_model)
    db.commit()
    return None


@router.get("/presets/list")
async def get_preset_templates():
    """获取预设模板列表"""
    return {
        "templates": [
            {
                "name": preset_data["name"],
                "provider": provider,
                "description": f"{preset_data['name']} - 包含 {len(preset_data['models'])} 个模型",
                "endpoint": preset_data["endpoint"],
                "available_models": [
                    {
                        "model_name": model["name"],
                        "display_name": model["display"],
                        "description": model["desc"]
                    }
                    for model in preset_data["models"]
                ]
            }
            for provider, preset_data in PROVIDER_PRESETS.items()
        ]
    }


@router.post("/quick-setup")
async def quick_setup_models(
    request: QuickSetupRequest,
    db: Session = Depends(get_db)
):
    """快速设置模型（从预设中批量创建）"""
    # 查找对应的预设模板
    if request.provider not in PROVIDER_PRESETS:
        raise HTTPException(status_code=400, detail=f"No preset found for provider: {request.provider}")
    
    preset = PROVIDER_PRESETS[request.provider]
    
    # 使用自定义端点或默认端点
    api_endpoint = request.endpoint if request.endpoint else preset["endpoint"]
    
    # 验证API端点
    if not validate_api_endpoint(api_endpoint):
        raise HTTPException(status_code=400, detail="Invalid API endpoint")
    
    # 加密API密钥
    encrypted_key = None
    if request.api_key:
        encrypted_key = encrypt_api_key(request.api_key)
    
    # 确定要创建的模型列表
    models_to_create = request.selected_models if request.selected_models else [
        model["name"] for model in preset["models"]
    ]
    
    created_models = []
    errors = []
    
    # 获取预设中可用的模型信息
    available_models_dict = {model["name"]: model for model in preset["models"]}
    
    for model_name in models_to_create:
        try:
            if model_name not in available_models_dict:
                errors.append(f"Model '{model_name}' not found in preset")
                continue
            
            model_info = available_models_dict[model_name]
            
            # 生成模型配置名称
            config_name = f"{preset['name']} - {model_info['display']}"
            
            # 检查名称是否已存在，如果存在则添加序号
            counter = 1
            original_name = config_name
            while db.query(ModelConfigDB).filter(ModelConfigDB.name == config_name).first():
                config_name = f"{original_name} ({counter})"
                counter += 1
            
            # 默认参数
            default_params = {
                "temperature": 0.7,
                "top_p": 1.0,
                "max_tokens": 1000,
                "frequency_penalty": 0,
                "presence_penalty": 0
            }
            
            # 创建模型配置
            db_model = ModelConfigDB(
                name=config_name,
                provider=request.provider,
                api_endpoint=api_endpoint,
                api_key=encrypted_key,
                model_name=model_name,
                default_params=default_params,
                tags=f"{request.provider}, preset",
                description=f"{model_info['desc']} - 从{preset['name']}预设自动创建"
            )
            
            db.add(db_model)
            db.flush()  # 获取ID但不提交
            
            created_models.append({
                "id": db_model.id,
                "name": db_model.name,
                "model_name": db_model.model_name,
                "provider": db_model.provider
            })
            
        except Exception as e:
            errors.append(f"Failed to create model '{model_name}': {str(e)}")
    
    # 提交所有成功的创建
    if created_models:
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to save models: {str(e)}")
    else:
        db.rollback()
    
    return {
        "success": True,
        "created_count": len(created_models),
        "failed_count": len(errors),
        "created_models": created_models,
        "errors": errors
    }


@router.post("/fetch-models")
async def fetch_models_from_endpoint(request: FetchModelsRequest):
    """从API端点获取可用模型列表"""
    try:
        # 构建模型列表端点
        models_endpoint = request.api_endpoint.rstrip('/')
        
        # 智能转换端点
        if models_endpoint.endswith('/models'):
            # 已经是models端点，直接使用
            pass
        elif models_endpoint.endswith('/chat/completions'):
            # 替换chat/completions为models
            models_endpoint = models_endpoint.replace('/chat/completions', '/models')
        elif models_endpoint.endswith('/v1'):
            # 如果已经以/v1结尾，直接添加/models
            models_endpoint = models_endpoint + '/models'
        else:
            # 其他情况，添加/models（对于已经包含/v1的路径）
            models_endpoint = models_endpoint + '/models'
        
        # 设置请求头
        headers = {
            "Content-Type": "application/json"
        }
        
        # 根据不同的提供商设置认证
        if request.api_key:
            if 'anthropic' in models_endpoint.lower():
                headers["x-api-key"] = request.api_key
            elif 'dashscope.aliyuncs.com' in models_endpoint.lower():
                headers["Authorization"] = f"Bearer {request.api_key}"
            else:
                headers["Authorization"] = f"Bearer {request.api_key}"
        
        print(f"正在请求端点: {models_endpoint}")  # 调试日志
        
        # 发送请求
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(models_endpoint, headers=headers)
            
            print(f"响应状态: {response.status_code}")  # 调试日志
            
            if response.status_code == 200:
                data = response.json()
                
                # 解析模型列表（适配不同API格式）
                models = []
                if 'data' in data and isinstance(data['data'], list):
                    # OpenAI格式
                    for model in data['data']:
                        if isinstance(model, dict) and 'id' in model:
                            models.append({
                                "id": model['id'],
                                "name": model.get('id', ''),
                                "display_name": model.get('id', ''),
                                "description": f"Model: {model.get('id', '')}",
                                "owned_by": model.get('owned_by', 'unknown')
                            })
                elif 'models' in data and isinstance(data['models'], list):
                    # 其他格式
                    for model in data['models']:
                        if isinstance(model, dict):
                            model_id = model.get('id') or model.get('name') or model.get('model')
                            if model_id:
                                models.append({
                                    "id": model_id,
                                    "name": model_id,
                                    "display_name": model_id,
                                    "description": f"Model: {model_id}",
                                    "owned_by": model.get('owned_by', 'unknown')
                                })
                elif isinstance(data, list):
                    # 直接是模型列表
                    for model in data:
                        if isinstance(model, str):
                            models.append({
                                "id": model,
                                "name": model,
                                "display_name": model,
                                "description": f"Model: {model}",
                                "owned_by": "unknown"
                            })
                        elif isinstance(model, dict):
                            model_id = model.get('id') or model.get('name') or str(model)
                            models.append({
                                "id": model_id,
                                "name": model_id,
                                "display_name": model_id,
                                "description": f"Model: {model_id}",
                                "owned_by": model.get('owned_by', 'unknown')
                            })
                
                print(f"解析到 {len(models)} 个模型")  # 调试日志
                
                return {
                    "success": True,
                    "endpoint": models_endpoint,
                    "models": models,
                    "total": len(models)
                }
            else:
                error_text = response.text
                print(f"请求失败: {response.status_code} - {error_text}")  # 调试日志
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {error_text}",
                    "endpoint": models_endpoint
                }
                
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "请求超时，请检查端点是否可访问",
            "endpoint": models_endpoint
        }
    except Exception as e:
        print(f"异常: {str(e)}")  # 调试日志
        return {
            "success": False,
            "error": f"获取模型列表失败: {str(e)}",
            "endpoint": models_endpoint
        }
