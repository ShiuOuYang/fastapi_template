from __future__ import annotations

from typing import Any, Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ApiResponse(BaseModel):
    """統一 API 回應格式。

    所有 route 都回傳這個外殼，前端只需處理一種結構。
    """

    success: bool = True
    data: Any = None
    message: str = ""


class PageParams(BaseModel):
    """分頁查詢參數。"""

    skip: int = Field(default=0, ge=0, description="略過筆數")
    limit: int = Field(default=50, ge=1, le=500, description="單頁最大筆數")


class Page(BaseModel, Generic[T]):
    """分頁結果容器，放進 ApiResponse.data。"""

    items: List[T]
    total: int
    skip: int
    limit: int
