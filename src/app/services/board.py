from __future__ import annotations

from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.board import Board
from app.repositories.board import BoardRepository
from app.schemas.board import BoardCreate, BoardUpdate


class BoardService:
    """Board 商業邏輯層。"""

    def __init__(self, session: AsyncSession) -> None:
        self.repository = BoardRepository(session)

    async def get_board(self, board_id: int) -> Optional[Board]:
        """取得單筆 Board。"""
        return await self.repository.get_by_id(board_id)

    async def get_all_boards(self) -> List[Board]:
        """取得所有 Board。"""
        return await self.repository.get_all()

    async def create_board(self, data: BoardCreate) -> Board:
        """建立新 Board。"""
        board = Board(
            board_name=data.board_name,
            panel_id=data.panel_id,
        )
        return await self.repository.create(board)

    async def update_board(
        self, board_id: int, data: BoardUpdate
    ) -> Optional[Board]:
        """更新 Board，若不存在回傳 None。"""
        board = await self.repository.get_by_id(board_id)
        if not board:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(board, field, value)
        return await self.repository.update(board)

    async def delete_board(self, board_id: int) -> bool:
        """刪除 Board，回傳是否成功。"""
        board = await self.repository.get_by_id(board_id)
        if not board:
            return False
        await self.repository.delete(board)
        return True
