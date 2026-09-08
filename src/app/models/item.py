from __future__ import annotations

from datetime import datetime
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Item(Base):
    """範例 ORM 模型。

    這是模板附的示範資料表，用來展示 model / schema / repository /
    service / route 的分層寫法。實際專案請刪除或改寫成自己的 model。
    """

    __tablename__ = "items"

    id: Mapped[int] = mapped_column(
        sa.Integer, primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(sa.NVARCHAR(200), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(
        sa.NVARCHAR(1000), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, server_default=sa.text("1")
    )
    created_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime, server_default=sa.text("GETDATE()"), nullable=True
    )
