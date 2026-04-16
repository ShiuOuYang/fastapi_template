from __future__ import annotations

"""Excel 資料驗證模組 — 定義欄位驗證規則與驗證結果。"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union


class DataType(str, Enum):
    """支援的資料型別列舉。"""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATE = "date"
    DATETIME = "datetime"


@dataclass
class ColumnRule:
    """
    單一欄位的驗證規則。

    Attributes:
        name: 欄位名稱（對應 Excel 表頭）。
        data_type: 預期的資料型別。
        required: 是否為必填欄位（不可為空）。
        min_value: 數值型欄位的最小值。
        max_value: 數值型欄位的最大值。
        min_length: 字串型欄位的最短長度。
        max_length: 字串型欄位的最長長度。
        allowed_values: 允許的值清單（enum 約束）。
        regex_pattern: 正則表達式驗證（僅字串）。
        custom_validator: 自訂驗證函式，接收值回傳 (bool, str)。
        aliases: 欄位名稱的別名清單（用於自動欄位對應）。
    """

    name: str
    data_type: DataType = DataType.STRING
    required: bool = False
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    allowed_values: Optional[List[Any]] = None
    regex_pattern: Optional[str] = None
    custom_validator: Optional[Callable[[Any], Tuple[bool, str]]] = None
    aliases: Optional[List[str]] = None


@dataclass
class CellError:
    """
    單一儲存格的驗證錯誤。

    Attributes:
        row: 行號（1-based，含表頭）。
        column: 欄位名稱。
        value: 實際值。
        error_type: 錯誤類型。
        message: 錯誤訊息。
    """

    row: int
    column: str
    value: Any
    error_type: str
    message: str


@dataclass
class ValidationResult:
    """
    整份資料的驗證結果。

    Attributes:
        is_valid: 是否全部通過驗證。
        total_rows: 總資料行數。
        error_count: 錯誤總數。
        errors: 所有錯誤的清單。
        warnings: 警告訊息清單。
    """

    is_valid: bool = True
    total_rows: int = 0
    error_count: int = 0
    errors: List[CellError] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def add_error(
        self,
        row: int,
        column: str,
        value: Any,
        error_type: str,
        message: str,
    ) -> None:
        """新增一筆驗證錯誤。"""
        self.errors.append(
            CellError(
                row=row,
                column=column,
                value=value,
                error_type=error_type,
                message=message,
            )
        )
        self.error_count += 1
        self.is_valid = False

    def add_warning(self, message: str) -> None:
        """新增一筆警告。"""
        self.warnings.append(message)

    def summary(self) -> Dict[str, Any]:
        """回傳驗證摘要字典。"""
        error_by_type: Dict[str, int] = {}
        error_by_column: Dict[str, int] = {}
        for err in self.errors:
            error_by_type[err.error_type] = (
                error_by_type.get(err.error_type, 0) + 1
            )
            error_by_column[err.column] = (
                error_by_column.get(err.column, 0) + 1
            )
        return {
            "is_valid": self.is_valid,
            "total_rows": self.total_rows,
            "error_count": self.error_count,
            "warning_count": len(self.warnings),
            "errors_by_type": error_by_type,
            "errors_by_column": error_by_column,
        }
