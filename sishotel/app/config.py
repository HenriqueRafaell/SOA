"""Configurações da aplicação carregadas via variáveis de ambiente."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "SisHotel"
    app_version: str = "1.0.0"
    environment: str = "development"
    database_url: str = "sqlite:///./sishotel.db"


settings = Settings()
