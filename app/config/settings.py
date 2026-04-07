from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # JWT
    jwt_secret_key = str
    jwt_algorithm = str
    jwt_access_token_expire_minutes = int

    # Database
    db_url: str

    # AWS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str
    s3_bucket_name: str

    # Other constants
    default_project_description: str = "No description provided"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()