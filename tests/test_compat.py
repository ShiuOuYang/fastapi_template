"""Python 3.8 / pandas 1.2.4 相容性回歸測試（不需要真實資料庫）。"""
from __future__ import annotations

import io

import pandas as pd
from httpx import AsyncClient
from sqlalchemy.dialects import mssql

from app.repositories.item import ItemRepository
from app.utils.excel_handler import dataframe_to_records


def test_dataframe_to_records_converts_nan_and_nat_to_none() -> None:
    """pandas 1.x 的 float / datetime 欄位，空值要轉成 None 才能輸出 JSON。"""
    df = pd.DataFrame(
        {
            "num": [1.5, None],
            "text": ["a", None],
            "date": pd.to_datetime(["2024-01-01", None]),
            "int": [1, 2],
        }
    )
    records = dataframe_to_records(df)

    assert records[1]["num"] is None
    assert records[1]["text"] is None
    assert records[1]["date"] is None
    # numpy.int64 要變成 Python int，pydantic 才序列化得了
    assert type(records[0]["int"]) is int


async def test_upload_excel_with_blank_cells(client: AsyncClient) -> None:
    """含空白儲存格的 Excel 上傳後應回 200，空值為 null。"""
    buffer = io.BytesIO()
    pd.DataFrame(
        {
            "數量": [1, None, 3],
            "名稱": ["甲", "乙", None],
            "日期": pd.to_datetime(["2024-01-01", None, "2024-03-01"]),
        }
    ).to_excel(buffer, index=False)
    buffer.seek(0)

    response = await client.post(
        "/api/v1/excel/upload",
        files={"file": ("blank.xlsx", buffer.getvalue())},
    )
    assert response.status_code == 200, response.text

    preview = response.json()["data"]["sheets"][0]["preview"]
    assert preview[1]["數量"] is None
    assert preview[1]["日期"] is None
    assert preview[2]["名稱"] is None


async def test_repository_list_sql_has_order_by() -> None:
    """SQL Server 的 OFFSET 必須搭配 ORDER BY，否則 SQLAlchemy 直接報錯。"""
    captured = []

    class _Result:
        def scalars(self):  # type: ignore[no-untyped-def]
            return self

        def all(self):  # type: ignore[no-untyped-def]
            return []

    class _FakeSession:
        async def execute(self, stmt):  # type: ignore[no-untyped-def]
            captured.append(stmt)
            return _Result()

    await ItemRepository(_FakeSession()).list(skip=20, limit=50)  # type: ignore[arg-type]

    sql = str(captured[0].compile(dialect=mssql.dialect()))
    assert "ORDER BY items.id" in sql
