from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]

class Settings(BaseSettings):
    app_name: str = "Enterprise IT Support Agentic RAG Copilot"
    app_env: str = "development"
    openai_api_key: str = ""
    openai_base_url: str = ""
    openai_api_base: str = ""
    tavily_api_key: str = ""
    pinecone_api_key: str = ""
    pinecone_index_name: str = "fde-it-support-rag"
    pinecone_namespace: str = "company-it-kb"
    embedding_model: str = "text-embedding-3-small"
    openai_model: str = "nex-n2.5-mini"
    top_k: int = 4
    max_retries: int = 1
    admin_api_key: str = "change-me"
    audit_db_path: str = str(BASE_DIR / "data" / "audit.db")
    upload_dir: str = str(BASE_DIR / "uploads")
    sample_kb_dir: str = str(BASE_DIR / "data" / "sample_kb")

    model_config = SettingsConfigDict(env_file=str(BASE_DIR / ".env"), extra="ignore")

    @property
    def effective_openai_base_url(self) -> str:
        # Support both OPENAI_BASE_URL (new SDK) and OPENAI_API_BASE (langchain)
        base = (self.openai_base_url or self.openai_api_base or "").strip()
        # Normalize: strip trailing slash, but keep /v1 if user provided it
        return base.rstrip("/") if base else ""




@lru_cache
def get_settings() -> Settings:
    return Settings()
