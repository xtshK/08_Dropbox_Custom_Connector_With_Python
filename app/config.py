from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    dropbox_app_key: str
    dropbox_app_secret: str
    dropbox_refresh_token: str
    host: str = "0.0.0.0"
    port: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
