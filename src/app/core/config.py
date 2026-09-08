from __future__ import annotations

from typing import List

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """應用程式環境設定，從 .env 檔載入。

    新增設定時，在這裡加一個欄位並在 .env.example 補上對應說明即可。
    """

    # ---------- 應用 ----------
    APP_NAME: str = "FastAPI Template"
    APP_DESCRIPTION: str = "FastAPI 專案模板"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    APP_PORT: int = 8000
    API_V1_PREFIX: str = "/api/v1"

    # 逗號分隔的允許來源；development 下預設全開
    CORS_ORIGINS: List[str] = []

    # ---------- 資料庫（SQL Server）----------
    DB_HOST: str = "localhost"
    DB_PORT: int = 1433
    DB_NAME: str = ""
    DB_USER: str = ""
    DB_PASSWORD: str = ""
    DB_DRIVER: str = "ODBC Driver 18 for SQL Server"
    DB_TRUST_SERVER_CERTIFICATE: bool = True
    DB_ECHO: bool = False

    # 啟動時是否依 model 自動建表。正式環境請保持 False，由 DBA 或 migration 管理。
    DB_AUTO_CREATE: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """允許 .env 用逗號分隔字串設定來源。"""
        if isinstance(value, str):
            return [v.strip() for v in value.split(",") if v.strip()]
        return value

    @property
    def is_development(self) -> bool:
        """是否為開發環境。"""
        return self.APP_ENV.lower() == "development"

    @property
    def database_url(self) -> str:
        """組合完整的 SQL Server 非同步連線字串。"""
        driver = self.DB_DRIVER.replace(" ", "+")
        trust = "yes" if self.DB_TRUST_SERVER_CERTIFICATE else "no"
        return (
            f"mssql+aioodbc://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
            f"?driver={driver}"
            f"&TrustServerCertificate={trust}"
        )

    @property
    def cors_origins(self) -> List[str]:
        """實際套用的 CORS 來源清單。"""
        if self.CORS_ORIGINS:
            return self.CORS_ORIGINS
        return ["*"] if self.is_development else []


settings = Settings()
