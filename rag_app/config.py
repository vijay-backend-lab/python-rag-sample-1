import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    mysql_url: str
    elasticsearch_url: str
    elasticsearch_index: str
    gemini_api_key: str | None
    gemini_model: str
    embedding_model: str
    embedding_dimensions: int
    third_party_url: str | None
    third_party_api_key: str | None
    third_party_source: str

    @classmethod
    def from_env(cls):
        return cls(os.getenv("MYSQL_URL", "mysql+pymysql://clinical_reader:change-me@localhost:3306/clinical_trials"), os.getenv("ELASTICSEARCH_URL", "http://localhost:9200"), os.getenv("ELASTICSEARCH_INDEX", "clinical-trial-knowledge"), os.getenv("GEMINI_API_KEY") or None, os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001"), int(os.getenv("EMBEDDING_DIMENSIONS", "768")), os.getenv("THIRD_PARTY_URL") or None, os.getenv("THIRD_PARTY_API_KEY") or None, os.getenv("THIRD_PARTY_SOURCE", "third-party"))
