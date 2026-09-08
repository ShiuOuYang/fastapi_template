from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.item import Item
from app.repositories.item import ItemRepository
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    """Item 商業邏輯層。

    Route 只處理 HTTP，Repository 只處理 SQL，
    所有判斷與流程組合寫在這一層。
    """

    def __init__(self, session: AsyncSession) -> None:
        self.repository = ItemRepository(session)

    async def get_item(self, item_id: int) -> Optional[Item]:
        """取得單筆 Item。"""
        return await self.repository.get_by_id(item_id)

    async def list_items(
        self, skip: int = 0, limit: int = 50
    ) -> Tuple[List[Item], int]:
        """分頁取得 Item 清單，同時回傳總筆數。"""
        items = await self.repository.list(skip=skip, limit=limit)
        total = await self.repository.count()
        return items, total

    async def create_item(self, data: ItemCreate) -> Item:
        """建立新 Item。"""
        item = Item(**data.model_dump())
        return await self.repository.create(item)

    async def update_item(
        self, item_id: int, data: ItemUpdate
    ) -> Optional[Item]:
        """部分更新 Item，若不存在回傳 None。"""
        item = await self.repository.get_by_id(item_id)
        if item is None:
            return None
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(item, field, value)
        return await self.repository.update(item)

    async def delete_item(self, item_id: int) -> bool:
        """刪除 Item，回傳是否有刪到資料。"""
        item = await self.repository.get_by_id(item_id)
        if item is None:
            return False
        await self.repository.delete(item)
        return True
