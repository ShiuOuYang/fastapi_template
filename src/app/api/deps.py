from __future__ import annotations

from typing_extensions import Annotated  # Python 3.8 的 typing 沒有 Annotated（3.9+ 才有）

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session

# 常用型別別名：在 route 簽章寫 `session: SessionDep` 即可。
SessionDep = Annotated[AsyncSession, Depends(get_session)]
