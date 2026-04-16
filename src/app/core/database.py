from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基底類別，所有 model 皆繼承此類別。"""
    pass


engine = create_async_engine(
    settings.database_url,
    echo=(settings.APP_ENV == "development"),
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends 用的 AsyncSession 產生器。"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """
    資料庫初始化框架。

    注意：本專案不使用 Base.metadata.create_all() 自動建表。
    資料表結構由 DBA 統一管理與部署。
    此函式保留作為未來初始化邏輯（如 seed data、連線測試）使用。
    """
    pass
