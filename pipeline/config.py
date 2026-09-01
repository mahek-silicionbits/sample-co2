from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # AWS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "eu-west-1"
    s3_bucket_name: str

    # MongoDB
    mongo_uri: str
    mongo_db_name: str = "sensor_pipeline"

    # Pipeline behavior
    batch_size: int = 100

    # S3 folder prefixes (matches our locked-in flow)
    raw_prefix: str = "raw/"
    raw_validated_prefix: str = "raw-validated/"
    raw_processed_prefix: str = "raw-processed/"
    raw_rejected_prefix: str = "raw-rejected/"
    processed_prefix: str = "processed/"

    class Config:
        env_file = ".env"


settings = Settings()