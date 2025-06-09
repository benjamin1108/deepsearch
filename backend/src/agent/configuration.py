import os
from pydantic import BaseModel, Field
from typing import Any, Optional, Literal, ClassVar

from langchain_core.runnables import RunnableConfig


class Configuration(BaseModel):
    """The configuration for the agent."""

    # LLM Provider configuration
    llm_provider: Literal["gemini", "openai", "qwen", "grok"] = Field(
        default="grok",
        metadata={
            "description": "The LLM provider to use (gemini, openai, qwen, grok)."
        },
    )

    query_generator_model: Optional[str] = Field(
        default=None,
        metadata={
            "description": "The name of the language model to use for the agent's query generation."
        },
    )

    reflection_model: Optional[str] = Field(
        default=None,
        metadata={
            "description": "The name of the language model to use for the agent's reflection."
        },
    )

    answer_model: Optional[str] = Field(
        default=None,
        metadata={
            "description": "The name of the language model to use for the agent's answer."
        },
    )

    # Model provider default configurations
    default_models: ClassVar[dict] = {
        "gemini": {
            "query_generator": "gemini-2.0-flash",
            "reflection": "gemini-2.5-flash-preview-04-17", 
            "answer": "gemini-2.5-pro-preview-05-06"
        },
        "openai": {
            "query_generator": "gpt-4o-mini",
            "reflection": "gpt-4o", 
            "answer": "gpt-4o"
        },
        "qwen": {
            "query_generator": "qwen-plus",
            "reflection": "qwen-max",
            "answer": "qwen-max"
        },
        "grok": {
            "query_generator": "grok-beta",
            "reflection": "grok-beta",
            "answer": "grok-beta"
        }
    }

    number_of_initial_queries: int = Field(
        default=3,
        metadata={"description": "The number of initial search queries to generate."},
    )

    max_research_loops: int = Field(
        default=2,
        metadata={"description": "The maximum number of research loops to perform."},
    )

    def model_post_init(self, __context: Any) -> None:
        """Set default models based on provider after initialization."""
        provider_defaults = self.default_models[self.llm_provider]
        
        if self.query_generator_model is None:
            self.query_generator_model = provider_defaults["query_generator"]
        if self.reflection_model is None:
            self.reflection_model = provider_defaults["reflection"]
        if self.answer_model is None:
            self.answer_model = provider_defaults["answer"]

    @classmethod
    def from_runnable_config(
        cls, config: Optional[RunnableConfig] = None
    ) -> "Configuration":
        """Create a Configuration instance from a RunnableConfig."""
        if not config:
            return cls()
            
        configurable = config.get("configurable", {})

        # Get raw values from config (priority) then environment variables (fallback)
        raw_values: dict[str, Any] = {}
        for name in cls.model_fields.keys():
            # Check config first (direct config values)
            if name in config:
                raw_values[name] = config[name]
            # Then check configurable
            elif name in configurable:
                raw_values[name] = configurable[name]
            # Finally check environment variables
            elif os.environ.get(name.upper()):
                raw_values[name] = os.environ.get(name.upper())

        # Filter out None values
        values = {k: v for k, v in raw_values.items() if v is not None}

        # Create instance with values (model_post_init will set defaults)
        return cls(**values)
