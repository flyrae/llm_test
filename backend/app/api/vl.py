from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import JSONResponse
from typing import Optional
import requests
import base64

router = APIRouter()

# Qwen-VL (OpenAI风格) API endpoint
QWEN_VL_API_URL = "http://localhost:8001/v1/chat/completions"  # 假设本地部署，端口和路径可调整
QWEN_VL_API_KEY = "YOUR_API_KEY"  # 如有需要

@router.post("/infer")
async def vl_infer(
    image: UploadFile = File(...),
    prompt: str = Form(...)
):
    # 读取图片并转base64
    image_bytes = await image.read()
    image_b64 = base64.b64encode(image_bytes).decode()
    
    # 构造OpenAI风格请求
    payload = {
        "model": "qwen-vl-plus",  # 或实际模型名
        "messages": [
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]}
        ]
    }
    headers = {"Content-Type": "application/json"}
    if QWEN_VL_API_KEY:
        headers["Authorization"] = f"Bearer {QWEN_VL_API_KEY}"
    
    # 调用Qwen-VL
    resp = requests.post(QWEN_VL_API_URL, json=payload, headers=headers)
    if resp.status_code == 200:
        result = resp.json()
        return JSONResponse(content=result)
    else:
        return JSONResponse(status_code=500, content={"error": resp.text})
