from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Environment
    env: str = "dev"

    # Database settings
    mongo_uri: str
    mongo_db: str

    # Root credentials (used for migrations, indexes, or admin tasks)
    mongo_initdb_root_username: str
    mongo_initdb_root_password: str

    # Optional: Mongo Express login for dev convenience
    mongo_express_user: str = "admin"
    mongo_express_password: str = "admin"
    mongo_express_port: int = 8081

    # Qdrant settings
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_api_url: str = None  # will be constructed automatically if not set
    qdrant_collection: str = "articles_embeddings"

    # LLM settings
    llm_model: str = "gemma3:1b"
    llm_base_url: str = "http://localhost:11434"

    # Full Mongo connection string (optional override)
    mongo_uri: str = (
        "mongodb://NewsBotAI:secret@localhost:27017/newsbotdb?authSource=admin"
    )

    # Application settings
    debug: bool = True
    environment: str = "development"

    # API settings
    api_v1_prefix: str = "/api/v1"
    project_name: str = "NewsBot AI"
    version: str = "1.0.0"

    # Security settings (for future use)
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    class Config:
        env_file = ".env"  # Path to your .env file
        env_file_encoding = "utf-8"
        case_sensitive = False
        env_nested_delimiter = "__"
        extra = "ignore"

    def model_post_init(self, __context):
        """
        pydantic v2 model post-init hook. Ensure derived values (like qdrant_api_url)
        are populated when not provided explicitly via env.
        """
        if not self.qdrant_api_url:
            # Prefer an explicit env var, otherwise construct from host/port
            object.__setattr__(
                self, "qdrant_api_url", f"http://{self.qdrant_host}:{self.qdrant_port}"
            )


# Create a global settings instance
settings = Settings()

# Debug: Print loaded settings
if settings.debug:
    print(
        f"🔧 Config loaded: ENV={settings.env}, MONGO_DB={settings.mongo_db}, QDRANT_API_URL={settings.qdrant_api_url}"
    )
