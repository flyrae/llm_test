"""预设的模型模板配置"""

# OpenAI模型模板
OPENAI_TEMPLATE = {
    "name": "OpenAI GPT Models",
    "provider": "openai",
    "api_endpoint": "https://api.openai.com/v1/chat/completions",
    "available_models": [
        {
            "model_name": "gpt-4",
            "display_name": "GPT-4",
            "description": "最强大的GPT-4模型，适合复杂任务",
            "default_params": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 1.0
            }
        },
        {
            "model_name": "gpt-4-turbo",
            "display_name": "GPT-4 Turbo",
            "description": "GPT-4的优化版本，更快更经济",
            "default_params": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 1.0
            }
        },
        {
            "model_name": "gpt-3.5-turbo",
            "display_name": "GPT-3.5 Turbo",
            "description": "经济高效的选择，适合大多数任务",
            "default_params": {
                "temperature": 0.7,
                "max_tokens": 4000,
                "top_p": 1.0
            }
        }
    ],
    "default_params": {
        "temperature": 0.7,
        "top_p": 1.0,
        "max_tokens": 1000,
        "frequency_penalty": 0,
        "presence_penalty": 0
    },
    "description": "OpenAI GPT系列模型的官方端点"
}

# Anthropic Claude模型模板
ANTHROPIC_TEMPLATE = {
    "name": "Anthropic Claude Models",
    "provider": "anthropic",
    "api_endpoint": "https://api.anthropic.com/v1/messages",
    "available_models": [
        {
            "model_name": "claude-3-opus-20240229",
            "display_name": "Claude 3 Opus",
            "description": "最强大的Claude模型，适合复杂推理任务",
            "default_params": {
                "temperature": 0.7,
                "max_tokens": 4000
            }
        },
        {
            "model_name": "claude-3-sonnet-20240229",
            "display_name": "Claude 3 Sonnet",
            "description": "平衡性能和成本的Claude模型",
            "default_params": {
                "temperature": 0.7,
                "max_tokens": 4000
            }
        },
        {
            "model_name": "claude-3-haiku-20240307",
            "display_name": "Claude 3 Haiku",
            "description": "最快最经济的Claude模型",
            "default_params": {
                "temperature": 0.7,
                "max_tokens": 4000
            }
        }
    ],
    "default_params": {
        "temperature": 0.7,
        "max_tokens": 1000
    },
    "description": "Anthropic Claude系列模型的官方端点"
}

# 本地Ollama模型模板
OLLAMA_TEMPLATE = {
    "name": "Local Ollama Models",
    "provider": "local",
    "api_endpoint": "http://localhost:11434/api/chat",
    "available_models": [
        {
            "model_name": "llama2",
            "display_name": "Llama 2",
            "description": "Meta的开源大语言模型",
            "default_params": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        },
        {
            "model_name": "codellama",
            "display_name": "Code Llama",
            "description": "专门用于代码生成的Llama模型",
            "default_params": {
                "temperature": 0.1,
                "num_predict": 2000
            }
        },
        {
            "model_name": "mistral",
            "display_name": "Mistral 7B",
            "description": "高效的开源模型",
            "default_params": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        },
        {
            "model_name": "qwen",
            "display_name": "Qwen",
            "description": "阿里巴巴的通义千问模型",
            "default_params": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        }
    ],
    "default_params": {
        "temperature": 0.7,
        "num_predict": 1000
    },
    "description": "本地Ollama服务器运行的模型"
}

# 所有预设模板
PRESET_TEMPLATES = [
    OPENAI_TEMPLATE,
    ANTHROPIC_TEMPLATE,
    OLLAMA_TEMPLATE
]