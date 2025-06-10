"""用于从不同提供商创建 LLM 实例的工厂。"""

import os
from typing import Optional, Any
from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI

try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

try:
    from langchain_community.chat_models import ChatTongyi
except ImportError:
    ChatTongyi = None




class LLMFactory:
    """用于从不同提供商创建 LLM 实例的工厂。"""

    @staticmethod
    def create_llm(
        provider: str,
        model_name: str,
        temperature: float = 0.0,
        max_retries: int = 2,
        **kwargs: Any
    ) -> BaseChatModel:
        """根据提供商创建 LLM 实例。
        
        Args:
            provider: LLM 提供商名称
            model_name: 特定的模型名称
            temperature: 采样温度
            max_retries: 最大重试次数
            **kwargs: 其他特定于提供商的参数
            
        Returns:
            BaseChatModel 实例
            
        Raises:
            ValueError: 如果提供商不受支持或缺少必需的包
            EnvironmentError: 如果未设置必需的 API 密钥
        """
        if provider == "gemini":
            return LLMFactory._create_gemini_llm(model_name, temperature, max_retries, **kwargs)
        elif provider == "openai":
            return LLMFactory._create_openai_llm(model_name, temperature, max_retries, **kwargs)
        elif provider == "qwen":
            return LLMFactory._create_qwen_llm(model_name, temperature, max_retries, **kwargs)
        elif provider == "grok":
            return LLMFactory._create_grok_llm(model_name, temperature, max_retries, **kwargs)
        else:
            raise ValueError(f"不支持的 LLM 提供商：{provider}")

    @staticmethod
    def _create_gemini_llm(
        model_name: str, 
        temperature: float, 
        max_retries: int, 
        **kwargs: Any
    ) -> ChatGoogleGenerativeAI:
        """创建 Gemini LLM 实例。"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("未设置 GEMINI_API_KEY 环境变量")
        
        return ChatGoogleGenerativeAI(
            model=model_name,
            temperature=temperature,
            max_retries=max_retries,
            api_key=api_key,
            **kwargs
        )

    @staticmethod
    def _create_openai_llm(
        model_name: str, 
        temperature: float, 
        max_retries: int, 
        **kwargs: Any
    ) -> BaseChatModel:
        """创建 OpenAI LLM 实例。"""
        if ChatOpenAI is None:
            raise ValueError("OpenAI 模型需要 langchain-openai 包。请使用以下命令安装：pip install langchain-openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("未设置 OPENAI_API_KEY 环境变量")
        
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_retries=max_retries,
            api_key=api_key,
            **kwargs
        )

    @staticmethod
    def _create_grok_llm(
        model_name: str, 
        temperature: float, 
        max_retries: int, 
        **kwargs: Any
    ) -> BaseChatModel:
        """使用与 OpenAI 兼容的 API 创建 Grok LLM 实例。"""
        if ChatOpenAI is None:
            raise ValueError("Grok 模型需要 langchain-openai 包。请使用以下命令安装：pip install langchain-openai")
        
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise EnvironmentError("Grok 模型需要 XAI_API_KEY 环境变量")
        
        return ChatOpenAI(
            model=model_name,
            temperature=temperature,
            max_retries=max_retries,
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            **kwargs
        )

    @staticmethod
    def _create_qwen_llm(
        model_name: str, 
        temperature: float, 
        max_retries: int, 
        **kwargs: Any
    ) -> BaseChatModel:
        """创建 Qwen LLM 实例。"""
        if ChatTongyi is None:
            raise ValueError("Qwen 模型需要 langchain-community 包。请使用以下命令安装：pip install langchain-community")
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise EnvironmentError("Qwen 模型需要 DASHSCOPE_API_KEY 环境变量")
        
        return ChatTongyi(
            model_name=model_name,
            temperature=temperature,
            dashscope_api_key=api_key,
            **kwargs
        )



    @staticmethod
    def get_supported_providers() -> list[str]:
        """获取支持的 LLM 提供商列表。"""
        return ["gemini", "openai", "qwen", "grok"]

    @staticmethod
    def check_provider_availability(provider: str) -> tuple[bool, Optional[str]]:
        """检查提供商是否可用（是否已安装必需的包并设置了环境变量）。
        
        Args:
            provider: 要检查的提供商名称
            
        Returns:
            一个元组 (is_available, error_message)
        """
        try:
            if provider == "gemini":
                if not os.getenv("GEMINI_API_KEY"):
                    return False, "未设置 GEMINI_API_KEY 环境变量"
                return True, None
            elif provider == "openai":
                if ChatOpenAI is None:
                    return False, "需要 langchain-openai 包。请使用以下命令安装：pip install langchain-openai"
                if not os.getenv("OPENAI_API_KEY"):
                    return False, "未设置 OPENAI_API_KEY 环境变量"
                return True, None
            elif provider == "qwen":
                if ChatTongyi is None:
                    return False, "需要 langchain-community 包。请使用以下命令安装：pip install langchain-community"
                if not os.getenv("DASHSCOPE_API_KEY"):
                    return False, "需要 DASHSCOPE_API_KEY 环境变量"
                return True, None
            elif provider == "grok":
                if ChatOpenAI is None:
                    return False, "需要 langchain-openai 包。请使用以下命令安装：pip install langchain-openai"
                if not os.getenv("XAI_API_KEY"):
                    return False, "需要 XAI_API_KEY 环境变量"
                return True, None
            else:
                return False, f"不支持的提供商：{provider}"
        except Exception as e:
            return False, str(e) 