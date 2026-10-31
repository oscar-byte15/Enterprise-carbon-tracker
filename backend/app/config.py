
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Authentication - Subsystem 1
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-me"
    )

    ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    # OpenAI configuration
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str | None = os.getenv("OPENAI_BASE_URL")

    # MongoDB configuration
    MONGODB_URI: str = os.getenv(
        "MONGODB_URI",
        "mongodb://127.0.0.1:27017"
    )

    MONGODB_DB: str = os.getenv(
        "MONGODB_DB",
        "enterprise_carbon_tracker"
    )


settings = Settings()
