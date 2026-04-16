from __future__ import annotations

from typing import Any

from pydantic import BaseModel


class ApiResponse(BaseModel):
    """統一 API 回應格式。"""

    success: bool = True
    data: Any = None
    message: str = ""
