"""Factory for creating LLM instances from different providers."""

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
    """Factory for creating LLM instances from different providers."""

    @staticmethod
    def create_llm(
        provider: str,
        model_name: str,
        temperature: float = 0.0,
        max_retries: int = 2,
        **kwargs: Any
    ) -> BaseChatModel:
        """Create an LLM instance based on the provider.
        
        Args:
            provider: The LLM provider name
            model_name: The specific model name
            temperature: Sampling temperature
            max_retries: Maximum number of retries
            **kwargs: Additional provider-specific arguments
            
        Returns:
            BaseChatModel instance
            
        Raises:
            ValueError: If provider is not supported or required package is missing
            EnvironmentError: If required API key is not set
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
            raise ValueError(f"Unsupported LLM provider: {provider}")

    @staticmethod
    def _create_gemini_llm(
        model_name: str, 
        temperature: float, 
        max_retries: int, 
        **kwargs: Any
    ) -> ChatGoogleGenerativeAI:
        """Create Gemini LLM instance."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError("GEMINI_API_KEY environment variable is not set")
        
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
        """Create OpenAI LLM instance."""
        if ChatOpenAI is None:
            raise ValueError("langchain-openai package is required for OpenAI models. Install with: pip install langchain-openai")
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY environment variable is not set")
        
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
        """Create Grok LLM instance using OpenAI-compatible API."""
        if ChatOpenAI is None:
            raise ValueError("langchain-openai package is required for Grok models. Install with: pip install langchain-openai")
        
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise EnvironmentError("XAI_API_KEY environment variable is required for Grok models")
        
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
        """Create Qwen LLM instance."""
        if ChatTongyi is None:
            raise ValueError("langchain-community package is required for Qwen models. Install with: pip install langchain-community")
        
        api_key = os.getenv("DASHSCOPE_API_KEY")
        if not api_key:
            raise EnvironmentError("DASHSCOPE_API_KEY environment variable is required for Qwen models")
        
        return ChatTongyi(
            model_name=model_name,
            temperature=temperature,
            dashscope_api_key=api_key,
            **kwargs
        ).bind(
            tools=kwargs.get("tools"),
            tool_choice="auto" if kwargs.get("tools") else None,
        )



    @staticmethod
    def get_supported_providers() -> list[str]:
        """Get list of supported LLM providers."""
        return ["gemini", "openai", "qwen", "grok"]

    @staticmethod
    def check_provider_availability(provider: str) -> tuple[bool, Optional[str]]:
        """Check if a provider is available (has required packages and env vars).
        
        Args:
            provider: The provider name to check
            
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            if provider == "gemini":
                if not os.getenv("GEMINI_API_KEY"):
                    return False, "GEMINI_API_KEY environment variable is not set"
                return True, None
            elif provider == "openai":
                if ChatOpenAI is None:
                    return False, "langchain-openai package is required. Install with: pip install langchain-openai"
                if not os.getenv("OPENAI_API_KEY"):
                    return False, "OPENAI_API_KEY environment variable is not set"
                return True, None
            elif provider == "qwen":
                if ChatTongyi is None:
                    return False, "langchain-community package is required. Install with: pip install langchain-community"
                if not os.getenv("DASHSCOPE_API_KEY"):
                    return False, "DASHSCOPE_API_KEY environment variable is required"
                return True, None
            elif provider == "grok":
                if ChatOpenAI is None:
                    return False, "langchain-openai package is required. Install with: pip install langchain-openai"
                if not os.getenv("XAI_API_KEY"):
                    return False, "XAI_API_KEY environment variable is required"
                return True, None
            else:
                return False, f"Unsupported provider: {provider}"
        except Exception as e:
            return False, str(e) 