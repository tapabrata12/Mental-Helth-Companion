import os  # Import os so tests can define safe default environment variables before app settings load.

os.environ.setdefault("PREFIX", "/api")  # Provide the API prefix expected by the FastAPI settings model.
os.environ.setdefault("MONGODB_URL", "mongodb://localhost:27017")  # Provide a harmless local MongoDB URL for tests that only import settings.
os.environ.setdefault("DATABASE_NAME", "mindbridge_test")  # Provide a test database name without touching production data.
os.environ.setdefault("USER_COLLECTION", "users")  # Provide the user collection name required by settings.
os.environ.setdefault("ASSESSMENT_COLLECTION_NAME", "assessments")  # Provide the assessment collection name required by settings.
os.environ.setdefault("JWT_SECRET", "test-secret-with-at-least-32-characters")  # Provide a test-only JWT secret that passes length validation.
os.environ.setdefault("JWT_ALGORITHM", "HS256")  # Provide the default JWT signing algorithm for token tests.
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "15")  # Provide the access-token lifetime expected by settings.
os.environ.setdefault("REFRESH_TOKEN_EXPIRE_DAYS", "7")  # Provide the refresh-token lifetime expected by settings.
os.environ.setdefault("CHROMA_COLLECTION_NAME", "mindbridge_test_knowledge")  # Provide a safe test-only ChromaDB collection name.
os.environ.setdefault("CHROMA_DIR", "./test_chroma_db")  # Provide a safe local test-only ChromaDB storage folder.