from __future__ import annotations

from typing import Any, Generic, List, Optional, Sequence, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """通用非同步 CRUD 資料存取層。

    子類別只要指定 `model`，就自動具備基本 CRUD；
    有額外查詢需求時再於子類別中加上專屬方法。

    注意：這一層只負責 flush，不負責 commit。
    commit / rollback 由 `get_session` 依賴統一處理，
    讓一個 request 內的多次寫入維持在同一個交易。
    """

    model: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, obj_id: Any) -> Optional[ModelT]:
        """依主鍵查詢單筆，不存在回傳 None。"""
        return await self.session.get(self.model, obj_id)

    async def list(self, skip: int = 0, limit: int = 50) -> List[ModelT]:
        """分頁查詢多筆。"""
        result = await self.session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def count(self) -> int:
        """計算總筆數。"""
        result = await self.session.execute(
            select(func.count()).select_from(self.model)
        )
        return int(result.scalar_one())

    async def create(self, obj: ModelT) -> ModelT:
        """新增一筆並取回資料庫產生的欄位（如自增 ID、預設值）。"""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def create_many(self, objs: Sequence[ModelT]) -> List[ModelT]:
        """批次新增。"""
        self.session.add_all(list(objs))
        await self.session.flush()
        return list(objs)

    async def update(self, obj: ModelT) -> ModelT:
        """更新一筆（呼叫前請先修改屬性）。"""
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelT) -> None:
        """刪除一筆。"""
        await self.session.delete(obj)
        await self.session.flush()
