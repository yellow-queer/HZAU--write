"""
Qwen API 配置模块

从 .env 文件读取配置并初始化 Qwen LLM
"""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_qwen_config() -> dict:
    """
    从 .env 文件加载 Qwen API 配置
    
    Returns:
        配置字典
    """
    # 加载 .env 文件
    env_path = Path(__file__).parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
    
    config = {
        "api_key": os.getenv("QWEN_API_KEY"),
        "base_url": os.getenv("QWEN_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1"),
        "model": os.getenv("QWEN_MODEL", "qwen-plus")
    }
    
    if not config["api_key"]:
        raise ValueError("QWEN_API_KEY 未在 .env 文件中配置")
    
    return config


def create_qwen_llm(model: str = "qwen-plus", temperature: float = 0.7):
    """
    创建 Qwen LLM 实例
    
    Args:
        model: 模型名称
        temperature: 温度参数
    
    Returns:
        LLM 实例
    """
    try:
        # 尝试使用 dashscope
        config = load_qwen_config()
        
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=config["api_key"],
            openai_api_base=config["base_url"],
            stop=None
        )
        
        print(f"已初始化 Qwen LLM: {model}")
        return llm
        
    except ImportError as e:
        print(f"警告：无法导入 Qwen 相关库：{e}")
        print("请运行：pip install dashscope openai langchain-openai")
        return None


def get_qwen_embedding_model(model_name: str = "text-embedding-v2"):
    """
    创建 Qwen 嵌入模型（LlamaIndex 兼容）
    
    Args:
        model_name: 嵌入模型名称
    
    Returns:
        LlamaIndex 兼容的嵌入模型实例
    """
    try:
        from llama_index.embeddings.openai import OpenAIEmbedding
        
        config = load_qwen_config()
        
        try:
            embed_model = OpenAIEmbedding(
                model=model_name,
                api_key=config["api_key"],
                api_base=config["base_url"],
                api_type="openai"
            )
            
            print(f"已初始化 Qwen Embedding: {model_name}")
            return embed_model
            
        except Exception as e:
            print(f"警告：Qwen 嵌入模型初始化失败：{e}")
            print("正在回退到 HuggingFace bge-small-zh-v1.5 模型...")
            
            try:
                from llama_index.embeddings.huggingface import HuggingFaceEmbedding
                
                embed_model = HuggingFaceEmbedding(
                    model_name="BAAI/bge-small-zh-v1.5"
                )
                
                print("已成功初始化 HuggingFace Embedding: bge-small-zh-v1.5")
                return embed_model
                
            except ImportError as hf_error:
                print(f"错误：无法导入 HuggingFace 嵌入模型：{hf_error}")
                print("请运行：pip install llama-index-embeddings-huggingface")
                return None
        
    except ImportError as e:
        print(f"警告：无法导入嵌入模型：{e}")
        return None
