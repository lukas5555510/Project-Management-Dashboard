from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    # JWT Configuration
    jwt_secret_key: str # The secret key used for signing JWTs
    jwt_algorithm: str = "HS256"# Default algorithm for JWT, can be overridden
    jwt_access_token_expire_minutes: int # Default expiration time for access tokens

    # Database Configuration
    postgres_user: str
    postgres_password: str
    postgres_host: str
    postgres_port: str
    postgres_db: str

    # AWS Configuration
    aws_access_key_id: str # AWS access key ID
    aws_secret_access_key: str # AWS secret access key
    aws_region: str# AWS region
    s3_bucket_name: str # S3 bucket name

    # Other Constants
    default_project_description: str = "No description provided"  # Default project description


# Instantiate the settings object
settings = Settings()