from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str = "redis://localhost:6379"
    DIGITRANSIT_API_KEY: str = ""
    GROQ_API_KEY: str = ""

    # Set USE_MOCK_SEED=true to skip the Digitransit API and seed from
    # local fixture data instead (useful when outside the EU).
    USE_MOCK_SEED: bool = False

    DIGITRANSIT_ROUTING_URL: str = (
        "https://api.digitransit.fi/routing/v1/routers/hsl/index/graphql"
    )
    GTFS_RT_BASE_URL: str = "https://realtime.hsl.fi/realtime"

<<<<<<< HEAD
=======
    # Comma-separated list of allowed CORS origins.
    # Use "*" for development. In production set to your frontend domain.
    BACKEND_CORS_ORIGINS: str = "*"

>>>>>>> 3e2bbc2 (feat(deployment): add AWS EC2 CI/CD and production deployment infrastructure)
    class Config:
        env_file = ".env"


settings = Settings()
