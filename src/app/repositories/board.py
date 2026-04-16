from __future__ import annotations

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board


class BoardRepository:
    """Board 資料存取層。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, board_id: int) -> Optional[Board]:
        """依 ID 查詢單筆 Board。"""
        result = await self.session.execute(
            select(Board).where(Board.id == board_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Board]:
        """查詢所有 Board。"""
        result = await self.session.execute(select(Board))
        return list(result.scalars().all())

    async def create(self, board: Board) -> Board:
        """新增一筆 Board。"""
        self.session.add(board)
        await self.session.flush()
        await self.session.refresh(board)
        return board

    async def update(self, board: Board) -> Board:
        """更新 Board（呼叫前請先修改屬性）。"""
        await self.session.flush()
        await self.session.refresh(board)
        return board

    async def delete(self, board: Board) -> None:
        """刪除一筆 Board。"""
        await self.session.delete(board)
        await self.session.flush()
