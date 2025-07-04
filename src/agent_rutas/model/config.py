"""
Configuration file for LLM models supported by the ModelFactory.

This module contains the mapping configuration between simplified model aliases
and their corresponding official model names and providers. It serves as a
central configuration point for all supported language models.

The MODEL_CONFIGS dictionary structure:
    - Key: The alias or shorthand name for the model (str)
    - Value: A dictionary containing:
        - provider: The service provider (e.g., "openai", "bedrock")
        - model_id: The official model identifier used by the provider

Example:
    To get the official model name for "gpt4":
    >>> MODEL_CONFIGS["gpt4"]["model_id"]
    'gpt-4'

    To check the provider:
    >>> MODEL_CONFIGS["claude-3-sonnet"]["provider"]
    'bedrock'
"""

OLLAMA_HOST = "192.168.0.155"#"127.0.0.1"

MODEL_CONFIGS = {
    # OpenAI models
    # These models use the OpenAI API and require an OpenAI API key
    "gpt4o": {"provider": "openai", "model_id": "gpt-4"},
    "gpt4omini": {"provider": "openai", "model_id": "gpt-4o-mini"},
    "gpt4": {"provider": "openai", "model_id": "gpt-4"},
    "gpt35": {"provider": "openai", "model_id": "gpt-3.5-turbo-0613"},
    "gpt-4": {"provider": "openai", "model_id": "gpt-4"},
    "gpt-3.5-turbo-0613": {"provider": "openai", "model_id": "gpt-3.5-turbo-0613"},
    # Bedrock models with inference profiles
    "claude-3-5-sonnet-v2": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "inference_profile_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    },
    # "claude-3-5-sonnet": {
    #     "provider": "bedrock",
    #     "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    #     "inference_profile_id": "us.anthropic.claude-3-5-sonnet-20240620-v1:0"
    # },
    "claude-3-5-sonnet": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-3-5-sonnet-20241022-v2:0",
        "inference_profile_id": "us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    },
    "claude-3-sonnet": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
        "inference_profile_id": "us.anthropic.claude-3-sonnet-20240229-v1:0",
    },
    # add nova pro model
    "nova-pro": {
        "provider": "bedrock",
        "model_id": "amazon.nova-pro-v1:0",
        "inference_profile_id": "us.amazon.nova-pro-v1:0",
    },
    # Bedrock models without inference profiles
    "claude-3-haiku": {
        "provider": "bedrock",
        "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
    },
    "claude-2": {"provider": "bedrock", "model_id": "anthropic.claude-v2:1"},
    

    # Ollama models
    "llama2": {
        "provider": "ollama",
        "model_id": "llama2",
        "endpoint": f"http://{OLLAMA_HOST}:11434/api/generate"
    },
    "llama31": {
        "provider": "ollama",
        "model_id": "llama3.1",
        "endpoint": f"http://{OLLAMA_HOST}:11434/api/generate"
    },
    "nemotron": {
        "provider": "ollama",
        "model_id": "nemotron",
        "endpoint": f"http://{OLLAMA_HOST}:11434/api/generate"
    },
    "deepseek-r1-32b": {
        "provider": "ollama",
        "model_id": "deepseek-r1:32b",
        "endpoint": f"http://{OLLAMA_HOST}:11434/api/generate"
    },
    "mistral":{
        "provider": "ollama",
        "model_id": "mistral",
        "endpoint": f"http://{OLLAMA_HOST}:11434/api/generate"
    },
    "granite3.2": {
        "provider": "ollama",
        "model_id": "granite3.2",
        "endpoint": f"http://{OLLAMA_HOST}:11434/api/generate"
    },
        # Google Gemini models
    # These models use Google's Generative AI API and require a GOOGLE_API_KEY
    "gemini-2.0-flash": {"provider": "google", "model_id": "gemini-2.0-flash"},
    "gemini-2.5-flash": {"provider": "google", "model_id": "gemini-2.5-flash-preview-04-17"},
    "gemini-2.5-pro": {"provider": "google", "model_id": "gemini-2.5-pro-preview-03-25"},
    "gemini-1.5-flash": {"provider": "google", "model_id": "gemini-1.5-flash"},
    "gemini-1.5-pro": {"provider": "google", "model_id": "gemini-1.5-pro"},
}

EMBEDDING_CONFIGS = {
    # OpenAI embeddings
    "text-embedding-3-small": {
        "provider": "openai",
        "model_id": "text-embedding-3-small",
    },
    "text-embedding-3-large": {
        "provider": "openai",
        "model_id": "text-embedding-3-large",
    },
    "text-embedding-ada-002": {
        "provider": "openai",
        "model_id": "text-embedding-ada-002",
    },
    # Bedrock embeddings
    "amazon-titan-embed": {
        "provider": "bedrock",
        "model_id": "amazon.titan-embed-text-v1",
    },
    "cohere-embed": {
        "provider": "bedrock",
        "model_id": "cohere.embed-english-v3",
    },
        # Google embeddings
    "google-embedding": {
        "provider": "google",
        "model_id": "text-embedding-004",
    },
}
