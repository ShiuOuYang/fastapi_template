from __future__ import annotations

from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ApiResponse(BaseModel):
    """統一 API 回應格式。

    所有 route 都回傳這個外殼，前端只需處理一種結構。
    """

    success: bool = True
    data: Any = None
    message: str = ""


class Page(BaseModel, Generic[T]):
    """分頁結果容器，放進 ApiResponse.data。"""

    items: List[T]
    total: int
    skip: int
    limit: int
