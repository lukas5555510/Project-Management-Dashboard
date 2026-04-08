from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # JWT Configuration
    jwt_secret_key: str = " "  # The secret key used for signing JWTs
    jwt_algorithm: str = "HS256"  # Default algorithm for JWT, can be overridden
    jwt_access_token_expire_minutes: int = 30  # Default expiration time for access tokens

    # Database Configuration
    db_url: str = "asdfasd" # Database connection URL

    # AWS Configuration
    aws_access_key_id: str = "sdfg"  # AWS access key ID
    aws_secret_access_key: str = "sdfg" # AWS secret access key
    aws_region: str = "sdfgd" # AWS region
    s3_bucket_name: str = "sdfgds" # S3 bucket name

    # Other Constants
    default_project_description: str = "No description provided"  # Default project description

    class Config:
        env_file = ".env"  # Specify the .env file to load environment variables from
        env_file_encoding = "utf-8"  # Encoding for the .env file

# Instantiate the settings object
settings = Settings()