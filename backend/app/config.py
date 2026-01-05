from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "Literature Review AI Assistant"
    database_url: str = "sqlite:///./literature_reviews.db"

    # DeepSeek API (OpenAI-compatible)
    deepseek_api_key: str = ""
    deepseek_base_url: str = "https://api.deepseek.com/v1"
    deepseek_model: str = "deepseek-chat"

    # PubMed settings
    pubmed_base_url: str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    pubmed_rate_limit: float = 0.34  # ~3 requests per second

    # Semantic Scholar settings
    semantic_scholar_base_url: str = "https://api.semanticscholar.org/graph/v1"
    semantic_scholar_api_key: str = ""  # Optional, for higher rate limits

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
