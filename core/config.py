"""
配置管理 - 支持 .env
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass
class Config:
    """全局配置"""
    
    model_name: str = "qwen-max"
    temperature: float = 0.7
    top_p: float = 0.8
    max_tokens: int = 2000
    verbose: bool = True
    dashscope_api_key: str = ""
    
    @classmethod
    def from_env(cls):
        """从环境变量加载配置（包括 .env）"""
        # 加载 .env 文件
        load_dotenv()
        
        return cls(
            dashscope_api_key=os.getenv("DASHSCOPE_API_KEY", ""),
            verbose=os.getenv("MINICLAW_VERBOSE", "true").lower() == "true",
            model_name=os.getenv("MINICLAW_MODEL", "qwen-max"),
            temperature=float(os.getenv("MINICLAW_TEMPERATURE", "0.7")),
            max_tokens=int(os.getenv("MINICLAW_MAX_TOKENS", "2000")),
        )