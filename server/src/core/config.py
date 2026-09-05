# File: server/src/core/config.py  # Full file path comment as requested

from pathlib import Path  # Import Path for stable env file resolution

from typing import Literal, Optional

from pydantic import Field, field_validator, model_validator  # Import Pydantic field tools and validators
from pydantic_settings import BaseSettings, SettingsConfigDict  # Import BaseSettings for env-driven config in Pydantic v2


BASE_DIR = Path(__file__).resolve().parents[2]  # Resolve project root from src/core/config.py
ENV_FILE = BASE_DIR / ".env"  # Point settings loading at Server/.env regardless of current working directory
choice = Literal['ollama', 'huggingface']


class Settings(BaseSettings):  # Define strongly validated application settings model
    model_config = SettingsConfigDict(env_file=ENV_FILE, env_file_encoding="utf-8", extra="ignore")  # Configure env file loading and ignore unrelated env vars

    PREFIX: str = Field(..., description="Global API prefix, e.g. /api")  # Require API route prefix from environment
    MONGODB_URL: str = Field(..., min_length=10, description="MongoDB connection URL")  # Require MongoDB connection string
    DATABASE_NAME: str = Field(..., min_length=1, description="MongoDB database name")  # Require target database name
    USER_COLLECTION: str = Field(..., min_length=1, description="MongoDB user collection name")  # Require collection name for user documents
    ASSESSMENT_COLLECTION_NAME: str = Field(..., min_length=1, description="Assessment collection name")  # Require collection name for user assessment
    CHROMA_COLLECTION_NAME: str = Field(..., min_length=1, description="Chroma collection name") # Require collection name for chroma vector store
    CHROMA_DIR: str = Field(..., min_length=1, description="Chroma directory") # Require for the path of the saved DB
    JWT_SECRET: str = Field(..., min_length=32, description="JWT signing secret (minimum 32 characters)")  # Require strong JWT secret length
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")  # Default JWT algorithm for token signing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=15, ge=1, le=1440, description="Access token expiry in minutes")  # Set secure practical default and bounds
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, ge=1, le=90, description="Refresh token expiry in days")  # Set bounded refresh token lifetime
    KNOWLEDGE_DIR: str = Field(..., min_length=1, description="Knowledge data directory")
    EMBEDDING_PROVIDER: choice = Field(..., min_length=6, description="Embedding provider")
    OLLAMA_EMBEDDING_MODEL: Optional[str] = Field(default=None, description="Ollama embedding model")
    OLLAMA_BASE_URL: Optional[str] = Field(default=None, min_length=1, description="Base URL for OLLAMA API")
    NVIDIA_API_KEY: Optional[str] = Field(default=None, min_length=1, description="NVIDIA API key")
    GEMINI_API_KEY: str = Field(..., min_length=1, description="GEMINI API key")
    GEMINI_MODEL: str = Field(..., min_length=1, description="GEMINI model")
    HUGGING_FACE_API_KEY: str = Field(..., min_length=1, description="Hugging face API key")
    HUGGING_FACE_EMBEDDING_MODEL: str = Field(..., min_length=1, description="Hugging face embedding model")

    @field_validator("PREFIX")  # Attach validator to API prefix field
    @classmethod  # Mark validator as class-level in Pydantic v2 style
    def validate_prefix(cls, value: str) -> str:  # Normalize and validate prefix value
        cleaned = value.strip()  # Remove surrounding whitespace from prefix
        if not cleaned.startswith("/"):  # Check prefix starts with slash
            cleaned = f"/{cleaned}"  # Autocorrect by prepending slash
        if cleaned.endswith("/") and len(cleaned) > 1:  # Check trailing slash for non-root values
            cleaned = cleaned.rstrip("/")  # Remove trailing slash to avoid double-slash route bugs
        return cleaned  # Return normalized API prefix

    @field_validator("JWT_ALGORITHM")  # Attach validator to JWT algorithm field
    @classmethod  # Mark validator as class-level method
    def validate_jwt_algorithm(cls, value: str) -> str:  # Enforce allowed JWT algorithm list
        allowed_algorithms = {"HS256", "HS384", "HS512"}  # Define supported symmetric HMAC algorithms
        normalized = value.strip().upper()  # Normalize whitespace and case for robust matching
        if normalized not in allowed_algorithms:  # Validate algorithm against allowed set
            raise ValueError(f"JWT_ALGORITHM must be one of {sorted(allowed_algorithms)}")  # Raise clear error for invalid algorithm
        return normalized  # Return normalized safe algorithm

    @field_validator("EMBEDDING_PROVIDER")  # Attach validator to embedding provider field
    @classmethod  # Mark validator as class-level in Pydantic v2 style
    def validate_embedding_provider(cls, value: str) -> str:  # Enforce allowed provider values
        allowed = {"ollama", "huggingface"}  # Define the supported provider strings
        normalized = value.strip().lower()  # Normalize whitespace and case
        if normalized not in allowed:  # Check the value is one of our two supported providers
            raise ValueError(f"EMBEDDING_PROVIDER must be one of {sorted(allowed)}")  # Raise clear error early
        return normalized  # Return the clean, validated value

    @model_validator(mode="after")
    def validate_provider_specific_settings(self):
        if self.EMBEDDING_PROVIDER == "ollama":
            missing = [
                name
                for name, value in {
                    "OLLAMA_EMBEDDING_MODEL": self.OLLAMA_EMBEDDING_MODEL,
                    "OLLAMA_BASE_URL": self.OLLAMA_BASE_URL,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"Missing required Ollama settings: {', '.join(missing)}")

        if self.EMBEDDING_PROVIDER == "huggingface":
            missing = [
                name
                for name, value in {
                    "HUGGING_FACE_API_KEY": self.HUGGING_FACE_API_KEY,
                    "HUGGING_FACE_EMBEDDING_MODEL": self.HUGGING_FACE_EMBEDDING_MODEL,
                }.items()
                if not value
            ]
            if missing:
                raise ValueError(f"Missing required Hugging Face settings: {', '.join(missing)}")

        return self


settings = Settings()  # Create singleton settings instance to import across the app
