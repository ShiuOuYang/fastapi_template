from __future__ import annotations

import logging
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """SQLAlchemy ORM 基底類別，所有 model 皆繼承此類別。"""

    pass


engine = create_async_engine(
    settings.database_url,
    echo=settings.DB_ECHO or settings.is_development,
    pool_pre_ping=True,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Depends 用的 AsyncSession 產生器。

    交易邊界在這裡：request 正常結束就 commit，拋例外就 rollback。
    因此 repository / service 只需要 flush，不要自己 commit。
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db() -> None:
    """啟動時的資料庫初始化。

    預設不自動建表（`DB_AUTO_CREATE=false`），資料表結構交由 DBA 或
    migration 工具管理。本機開發想快速起步時，可把 `DB_AUTO_CREATE`
    設為 true 讓 SQLAlchemy 依 model 建表。
    """
    if not settings.DB_AUTO_CREATE:
        return

    # 匯入 models 讓 Base.metadata 收集到所有資料表定義
    import app.models  # noqa: F401

    logger.info("DB_AUTO_CREATE 已開啟，正在建立資料表……")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """關閉連線池，於應用程式結束時呼叫。"""
    await engine.dispose()
