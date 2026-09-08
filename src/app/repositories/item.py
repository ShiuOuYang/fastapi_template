from __future__ import annotations

from typing import List

from sqlalchemy import select

from app.models.item import Item
from app.repositories.base import BaseRepository


class ItemRepository(BaseRepository[Item]):
    """Item 資料存取層。

    基本 CRUD 由 BaseRepository 提供，這裡只放 Item 專屬查詢。
    """

    model = Item

    async def get_by_name(self, name: str) -> List[Item]:
        """依名稱模糊查詢（示範自訂查詢的寫法）。"""
        result = await self.session.execute(
            select(Item).where(Item.name.like(f"%{name}%"))
        )
        return list(result.scalars().all())
