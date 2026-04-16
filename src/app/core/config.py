from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """應用程式環境設定，從 .env 檔載入。"""

    DB_HOST: str = "localhost"
    DB_PORT: int = 1433
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    APP_ENV: str = "development"
    APP_PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    @property
    def database_url(self) -> str:
        """組合完整的 SQL Server 非同步連線字串。"""
        return (
            f"mssql+aioodbc://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver=ODBC+Driver+18+for+SQL+Server"
            f"&TrustServerCertificate=yes"
        )


settings = Settings()
