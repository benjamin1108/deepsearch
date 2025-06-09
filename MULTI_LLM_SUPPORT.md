# 多LLM提供商支持

本项目现已支持多种大语言模型提供商，包括Google Gemini、OpenAI、阿里巴巴通义千问和Grok。

## 支持的LLM提供商

### 1. Google Gemini (默认)
- **模型**: gemini-2.0-flash, gemini-2.5-flash-preview-04-17, gemini-2.5-pro-preview-05-06
- **特点**: 内置Google搜索功能，无需额外搜索API
- **配置**: 需要 `GEMINI_API_KEY`

### 2. OpenAI
- **模型**: gpt-4o-mini, gpt-4o, gpt-4-turbo
- **特点**: 强大的推理能力
- **配置**: 需要 `OPENAI_API_KEY` 和搜索API

### 3. 阿里巴巴通义千问
- **模型**: qwen-plus, qwen-max
- **特点**: 中文理解能力强
- **配置**: 需要 `DASHSCOPE_API_KEY` 和搜索API

### 4. Grok
- **模型**: grok-beta
- **特点**: 创新的AI推理能力
- **配置**: 需要 `XAI_API_KEY` 和搜索API

## 环境配置

### 基础配置
```bash
# 选择LLM提供商 (gemini, openai, qwen, grok)
LLM_PROVIDER=gemini

# Google Gemini (默认提供商)
GEMINI_API_KEY=your_gemini_api_key_here

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here

# 通义千问
DASHSCOPE_API_KEY=your_dashscope_api_key_here

# Grok
XAI_API_KEY=your_xai_api_key_here
```

### 搜索API配置 (非Gemini提供商需要)

由于只有Gemini具有内置的Google搜索功能，其他提供商需要配置外部搜索API：

#### 选项1: Google Custom Search API (推荐)
```bash
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_CX=your_google_custom_search_engine_id_here
```

#### 选项2: SerpAPI
```bash
SERPAPI_API_KEY=your_serpapi_key_here
```

#### 选项3: Bing Search API
```bash
BING_SEARCH_API_KEY=your_bing_search_api_key_here
```

## 安装依赖

### 基础安装
```bash
cd backend
pip install .
```

### 安装特定提供商的依赖
```bash
# OpenAI和Grok
pip install ".[openai]"

# 通义千问
pip install ".[community]"
pip install dashscope

# 安装所有提供商支持
pip install ".[all]"
```

## 使用方法

### 1. 通过环境变量配置
在 `backend/.env` 文件中设置：
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key_here
GOOGLE_API_KEY=your_google_key_here
GOOGLE_CX=your_google_cx_here
```

### 2. 通过前端界面选择
在前端界面中，您可以：
- 选择LLM提供商 (Google Gemini, OpenAI, Qwen, Grok)
- 选择具体模型
- 设置研究强度 (低、中、高)

### 3. 通过API配置
```python
from agent.configuration import Configuration

config = Configuration(
    llm_provider="openai",
    query_generator_model="gpt-4o-mini",
    reflection_model="gpt-4o",
    answer_model="gpt-4o"
)
```

## 模型推荐

### 性能优先
- **Gemini**: gemini-2.5-pro-preview-05-06
- **OpenAI**: gpt-4o
- **Qwen**: qwen-max
- **Grok**: grok-beta

### 速度优先
- **Gemini**: gemini-2.0-flash
- **OpenAI**: gpt-4o-mini
- **Qwen**: qwen-plus
- **Grok**: grok-beta

### 成本优先
- **Gemini**: gemini-2.0-flash
- **OpenAI**: gpt-4o-mini
- **Qwen**: qwen-plus
- **Grok**: grok-beta

## 故障排除

### 1. 检查提供商可用性
```python
from agent.llm_factory import LLMFactory

# 检查所有支持的提供商
providers = LLMFactory.get_supported_providers()
print(f"支持的提供商: {providers}")

# 检查特定提供商是否可用
is_available, error = LLMFactory.check_provider_availability("openai")
if not is_available:
    print(f"OpenAI不可用: {error}")
```

### 2. 检查搜索API可用性
```python
from agent.search_utils import SearchUtils

# 检查可用的搜索API
available_apis = SearchUtils.get_available_search_apis()
print(f"可用的搜索API: {available_apis}")
```

### 3. 常见错误

#### API密钥未设置
```
EnvironmentError: OPENAI_API_KEY environment variable is not set
```
**解决方案**: 在 `.env` 文件中设置相应的API密钥

#### 缺少依赖包
```
ValueError: langchain-openai package is required for OpenAI models
```
**解决方案**: 安装相应的依赖包 `pip install langchain-openai`

#### 搜索API未配置
```
Warning: No search API configured
```
**解决方案**: 配置至少一个搜索API (Google Custom Search, SerpAPI, 或 Bing Search)

## 性能对比

| 提供商 | 查询生成 | 反思分析 | 答案合成 | 搜索集成 | 中文支持 |
|--------|----------|----------|----------|----------|----------|
| Gemini | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| OpenAI | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| Anthropic | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| Qwen | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| ERNIE | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

## 贡献

欢迎为项目添加更多LLM提供商支持！请参考 `agent/llm_factory.py` 中的实现模式。 