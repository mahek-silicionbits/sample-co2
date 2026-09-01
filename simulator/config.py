from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "eu-west-1"
    s3_bucket_name: str
    raw_prefix: str = "raw/"

    class Config:
        env_file = ".env"


settings = Settings()