from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.base import ApiResponse
from app.schemas.board import BoardCreate, BoardResponse, BoardUpdate
from app.services.board import BoardService

router = APIRouter(prefix="/boards", tags=["Board"])


def get_board_service(
    session: AsyncSession = Depends(get_session),
) -> BoardService:
    """依賴注入：取得 BoardService 實例。"""
    return BoardService(session)


@router.get("", response_model=ApiResponse)
async def get_boards(
    service: BoardService = Depends(get_board_service),
) -> ApiResponse:
    """取得所有板子。"""
    boards = await service.get_all_boards()
    return ApiResponse(
        data=[BoardResponse.model_validate(b) for b in boards],
    )


@router.get("/{board_id}", response_model=ApiResponse)
async def get_board(
    board_id: int,
    service: BoardService = Depends(get_board_service),
) -> ApiResponse:
    """依 ID 取得單筆板子。"""
    board = await service.get_board(board_id)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return ApiResponse(data=BoardResponse.model_validate(board))


@router.post("", response_model=ApiResponse, status_code=201)
async def create_board(
    data: BoardCreate,
    service: BoardService = Depends(get_board_service),
) -> ApiResponse:
    """建立新板子。"""
    board = await service.create_board(data)
    return ApiResponse(
        data=BoardResponse.model_validate(board),
        message="Board created",
    )


@router.put("/{board_id}", response_model=ApiResponse)
async def update_board(
    board_id: int,
    data: BoardUpdate,
    service: BoardService = Depends(get_board_service),
) -> ApiResponse:
    """更新板子。"""
    board = await service.update_board(board_id, data)
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return ApiResponse(
        data=BoardResponse.model_validate(board),
        message="Board updated",
    )


@router.delete("/{board_id}", response_model=ApiResponse)
async def delete_board(
    board_id: int,
    service: BoardService = Depends(get_board_service),
) -> ApiResponse:
    """刪除板子。"""
    deleted = await service.delete_board(board_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Board not found")
    return ApiResponse(message="Board deleted")
