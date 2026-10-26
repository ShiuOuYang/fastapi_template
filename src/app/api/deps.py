from __future__ import annotations

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated  # typing.Annotated 需 Python 3.9+

from app.core.database import get_session

# 常用型別別名：在 route 簽章寫 `session: SessionDep` 即可。
SessionDep = Annotated[AsyncSession, Depends(get_session)]
