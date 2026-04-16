# ExcelHandler 使用手冊

通用 Excel 資料處理工具，涵蓋讀取、寫入、驗證、合併、圖表五大功能。

---

## 目錄

- [檔案結構](#檔案結構)
- [安裝依賴](#安裝依賴)
- [快速開始](#快速開始)
- [一、讀取 Excel](#一讀取-excel)
  - [1.1 讀取單一 Sheet](#11-讀取單一-sheet)
  - [1.2 讀取所有 Sheet](#12-讀取所有-sheet)
  - [1.3 大檔案串流讀取](#13-大檔案串流讀取)
  - [1.4 查看 Sheet 資訊](#14-查看-sheet-資訊)
- [二、自動偵測 / 欄位對應](#二自動偵測--欄位對應)
  - [2.1 偵測欄位資訊](#21-偵測欄位資訊)
  - [2.2 自動欄位對應（別名匹配）](#22-自動欄位對應別名匹配)
- [三、資料驗證](#三資料驗證)
  - [3.1 驗證規則定義](#31-驗證規則定義)
  - [3.2 執行驗證](#32-執行驗證)
  - [3.3 驗證結果說明](#33-驗證結果說明)
  - [3.4 支援的驗證類型](#34-支援的驗證類型)
- [四、寫入 Excel](#四寫入-excel)
  - [4.1 基本寫入（帶美化格式）](#41-基本寫入帶美化格式)
  - [4.2 多 Sheet 寫入](#42-多-sheet-寫入)
  - [4.3 輸出為 BytesIO（API 下載用）](#43-輸出為-bytesioapi-下載用)
- [五、合併](#五合併)
  - [5.1 合併多個 Excel 檔案](#51-合併多個-excel-檔案)
  - [5.2 合併同檔多個 Sheet](#52-合併同檔多個-sheet)
- [六、圖表生成](#六圖表生成)
- [七、樣式預設](#七樣式預設)
- [八、完整管線範例](#八完整管線範例)
- [九、FastAPI 整合範例](#九fastapi-整合範例)
- [API 速查表](#api-速查表)

---

## 檔案結構

```
src/app/utils/
├── excel_handler.py       # 主類別 ExcelHandler
├── excel_validation.py    # 驗證規則 ColumnRule / ValidationResult
├── excel_styles.py        # 樣式預設 / 圖表工具
└── excel_examples.py      # 9 個可執行範例
```

## 安裝依賴

```bash
pip install pandas>=1.5.0,<2.0.0 openpyxl>=3.1.0,<3.2.0
```

> 已包含在 `requirements.txt` 中。

---

## 快速開始

```python
from app.utils.excel_handler import ExcelHandler
from app.utils.excel_validation import ColumnRule, DataType
from app.utils.excel_styles import ChartType

# 讀取
handler = ExcelHandler("data/report.xlsx")
df = handler.read_sheet()

# 寫入
handler = ExcelHandler()
handler.write(data=df, output_path="output/result.xlsx")
```

---

## 一、讀取 Excel

### 1.1 讀取單一 Sheet

```python
handler = ExcelHandler("data/test.xlsx")

# 自動偵測表頭
df = handler.read_sheet()

# 指定 Sheet 名稱
df = handler.read_sheet(sheet_name="原始資料")

# 指定 Sheet 索引（0-based）
df = handler.read_sheet(sheet_name=1)

# 手動指定表頭行（0-based），跳過前 2 行
df = handler.read_sheet(header_row=2)

# 只讀取特定欄位
df = handler.read_sheet(use_cols=["姓名", "分數"])

# 強制指定欄位型別
df = handler.read_sheet(dtype={"員工編號": str, "金額": float})
```

**參數一覽：**

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `sheet_name` | `str \| int` | `0` | Sheet 名稱或索引 |
| `header_row` | `int \| None` | `None` | 表頭行號（0-based），None 自動偵測 |
| `skip_rows` | `List[int]` | `None` | 要跳過的行號清單 |
| `use_cols` | `List[str]` | `None` | 只讀取指定欄位 |
| `dtype` | `Dict` | `None` | 強制欄位型別 |
| `na_values` | `List[str]` | `None` | 額外視為空值的字串 |

### 1.2 讀取所有 Sheet

```python
handler = ExcelHandler("data/multi_sheet.xlsx")
all_dfs = handler.read_all_sheets()

# 回傳 Dict：{"Sheet1": DataFrame, "Sheet2": DataFrame, ...}
for name, df in all_dfs.items():
    print(f"{name}: {len(df)} 行 x {len(df.columns)} 欄")
```

### 1.3 大檔案串流讀取

適用於幾十萬行以上的 Excel，**不會一次載入整個檔案到記憶體**。

```python
handler = ExcelHandler("data/huge_file.xlsx")

for chunk_df in handler.read_large_file(chunk_size=5000):
    print(f"本批次 {len(chunk_df)} 行")
    # 逐批處理，例如寫入 DB
```

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `sheet_name` | `str \| int` | `0` | Sheet 名稱或索引 |
| `chunk_size` | `int` | `10000` | 每批行數 |
| `header_row` | `int` | `0` | 表頭行號 |

### 1.4 查看 Sheet 資訊

```python
handler = ExcelHandler("data/test.xlsx")

# 取得所有 Sheet 名稱
names = handler.get_sheet_names()
# ['Sheet1', 'Sheet2', '彙總']

# 取得各 Sheet 行列數
info = handler.get_sheet_info()
# [{'name': 'Sheet1', 'max_row': 500, 'max_column': 8}, ...]
```

---

## 二、自動偵測 / 欄位對應

### 2.1 偵測欄位資訊

當你不確定 Excel 裡有什麼欄位時，用這個功能掃描：

```python
handler = ExcelHandler("data/unknown.xlsx")
columns = handler.detect_columns()

for col in columns:
    print(f"欄位: {col['name']}")
    print(f"  推斷型別: {col['inferred_type']}")
    print(f"  非空率:   {col['non_null_rate']}%")
    print(f"  唯一值:   {col['unique_count']}")
    print(f"  範例:     {col['sample_values'][:3]}")
```

**回傳欄位：**

| 欄位 | 說明 |
|------|------|
| `name` | 欄位名稱 |
| `inferred_type` | 推斷型別（string / integer / float / datetime / boolean / unknown） |
| `non_null_rate` | 非空率（%） |
| `non_null_count` | 非空筆數 |
| `total_count` | 總筆數 |
| `unique_count` | 唯一值數量 |
| `sample_values` | 前 5 個非空樣本值 |

### 2.2 自動欄位對應（別名匹配）

Excel 欄位名可能是英文、中文、縮寫各種寫法，用別名自動匹配：

```python
rules = [
    ColumnRule(name="板子名稱", aliases=["Board Name", "board_name", "PCB"]),
    ColumnRule(name="測試值",  aliases=["Test Value", "value", "量測值"]),
    ColumnRule(name="操作員",  aliases=["Operator", "OP", "作業員"]),
]

handler = ExcelHandler("data/report.xlsx")
df = handler.read_sheet()

mapping = handler.auto_map_columns(rules, df=df)
# {'板子名稱': 'Board Name', '測試值': 'Test Value', '操作員': 'Operator'}
# 找不到的欄位（如 Excel 中沒有操作員相關欄位）不會出現在結果中
```

> 比對邏輯：不分大小寫，去除前後空白。

---

## 三、資料驗證

### 3.1 驗證規則定義

用 `ColumnRule` 定義每個欄位的驗證條件：

```python
from app.utils.excel_validation import ColumnRule, DataType

rule = ColumnRule(
    name="員工編號",           # 欄位名稱
    data_type=DataType.STRING, # 預期型別
    required=True,             # 必填
    min_length=4,              # 最短 4 字元
    max_length=10,             # 最長 10 字元
    regex_pattern=r"^E\d+$",  # 格式：E 開頭 + 數字
    allowed_values=None,       # 允許值清單（None 不限制）
    aliases=["EmpID", "工號"], # 別名（for auto_map_columns）
    custom_validator=None,     # 自訂驗證函式
)
```

**ColumnRule 參數一覽：**

| 參數 | 型別 | 預設 | 適用型別 | 說明 |
|------|------|------|----------|------|
| `name` | `str` | 必填 | 全部 | 欄位名稱 |
| `data_type` | `DataType` | `STRING` | 全部 | 預期型別 |
| `required` | `bool` | `False` | 全部 | 是否必填 |
| `min_value` | `float` | `None` | INTEGER, FLOAT | 最小值 |
| `max_value` | `float` | `None` | INTEGER, FLOAT | 最大值 |
| `min_length` | `int` | `None` | STRING | 最短長度 |
| `max_length` | `int` | `None` | STRING | 最長長度 |
| `allowed_values` | `List` | `None` | 全部 | 允許的值清單 |
| `regex_pattern` | `str` | `None` | STRING | 正則表達式 |
| `custom_validator` | `Callable` | `None` | 全部 | 自訂驗證函式 |
| `aliases` | `List[str]` | `None` | — | 別名（用於 auto_map_columns） |

**DataType 列舉：**

| 值 | 說明 | Python 型別 |
|------|------|-------------|
| `STRING` | 字串 | `str` |
| `INTEGER` | 整數 | `int` |
| `FLOAT` | 浮點數 | `float` |
| `BOOLEAN` | 布林值 | `bool`（也接受 "yes"/"no"/"1"/"0"/"是"/"否"） |
| `DATE` | 日期 | `datetime` |
| `DATETIME` | 日期時間 | `datetime` |

### 3.2 執行驗證

```python
handler = ExcelHandler("data/import.xlsx")
df = handler.read_sheet()

rules = [
    ColumnRule(name="員工編號", data_type=DataType.STRING, required=True, regex_pattern=r"^E\d{3}$"),
    ColumnRule(name="年齡", data_type=DataType.INTEGER, required=True, min_value=18, max_value=100),
    ColumnRule(name="部門", data_type=DataType.STRING, allowed_values=["製造", "品保", "研發"]),
]

# 基本驗證
result = handler.validate(df, rules)

# 搭配欄位對應使用
mapping = handler.auto_map_columns(rules, df=df)
result = handler.validate(df, rules, column_mapping=mapping)

# 限制最多收集 500 筆錯誤（避免大檔案記憶體爆炸）
result = handler.validate(df, rules, max_errors=500)
```

**自訂驗證函式：**

```python
def check_not_zero(value):
    """值不可為零。回傳 (是否通過, 錯誤訊息)。"""
    return (value != 0, "值不可為零")

rule = ColumnRule(
    name="分數",
    data_type=DataType.FLOAT,
    custom_validator=check_not_zero,
)
```

### 3.3 驗證結果說明

```python
result = handler.validate(df, rules)

# 基本屬性
result.is_valid      # bool：是否全部通過
result.total_rows    # int：總資料行數
result.error_count   # int：錯誤總數
result.errors        # List[CellError]：所有錯誤
result.warnings      # List[str]：警告訊息

# 遍歷每筆錯誤
for err in result.errors:
    print(f"行 {err.row}, 欄 {err.column}: [{err.error_type}] {err.message}")
    # 行 3, 欄 年齡: [max_value] 欄位 '年齡' 值 150.0 大於最大值 100

# 取得統計摘要
summary = result.summary()
# {
#     'is_valid': False,
#     'total_rows': 100,
#     'error_count': 5,
#     'warning_count': 0,
#     'errors_by_type': {'required': 2, 'max_value': 1, 'regex': 2},
#     'errors_by_column': {'員工編號': 2, '年齡': 1, 'email': 2}
# }
```

### 3.4 支援的驗證類型

| error_type | 觸發條件 |
|------------|----------|
| `required` | 必填欄位但值為空 |
| `type` | 值無法轉換為指定型別 |
| `min_value` | 數值小於最小值 |
| `max_value` | 數值大於最大值 |
| `min_length` | 字串長度不足 |
| `max_length` | 字串長度超過 |
| `allowed_values` | 值不在允許清單中 |
| `regex` | 字串不符合正則表達式 |
| `custom` | 自訂驗證函式回傳失敗 |

---

## 四、寫入 Excel

### 4.1 基本寫入（帶美化格式）

```python
handler = ExcelHandler()

# 接受 List[Dict]
data = [
    {"姓名": "王小明", "分數": 92.5},
    {"姓名": "李大華", "分數": 88.0},
]
handler.write(data=data, output_path="output/report.xlsx")

# 也接受 DataFrame
import pandas as pd
df = pd.DataFrame(data)
handler.write(data=df, output_path="output/report.xlsx")
```

**自動美化效果：**
- ✅ 藍底白字粗體表頭
- ✅ 所有儲存格加框線
- ✅ 自動調整欄寬（支援中文字寬計算）
- ✅ 凍結第一行（表頭固定）
- ✅ 啟用自動篩選

**參數一覽：**

| 參數 | 型別 | 預設 | 說明 |
|------|------|------|------|
| `data` | `DataFrame \| List[Dict]` | 必填 | 來源資料 |
| `output_path` | `str \| Path \| None` | `None` | 輸出路徑，None 回傳 BytesIO |
| `sheet_name` | `str` | `"Sheet1"` | 工作表名稱 |
| `style_header` | `bool` | `True` | 套用表頭樣式 |
| `style_data` | `bool` | `True` | 套用資料欄樣式 |
| `auto_width` | `bool` | `True` | 自動調整欄寬 |
| `freeze_panes` | `str \| None` | `"A2"` | 凍結窗格位置 |
| `auto_filter` | `bool` | `True` | 啟用自動篩選 |

### 4.2 多 Sheet 寫入

```python
handler = ExcelHandler()
handler.write_multiple_sheets(
    sheets={
        "Q1": df_q1,
        "Q2": df_q2,
        "年度彙總": [{"項目": "總營收", "金額": 5000000}],  # List[Dict] 也行
    },
    output_path="output/年度報表.xlsx",
)
```

### 4.3 輸出為 BytesIO（API 下載用）

```python
handler = ExcelHandler()
buffer = handler.write(data=df, output_path=None)  # 不傳路徑 → 回傳 BytesIO
# buffer 可直接給 FastAPI StreamingResponse（見第九章）
```

---

## 五、合併

### 5.1 合併多個 Excel 檔案

```python
handler = ExcelHandler()
merged_df = handler.merge_files(
    file_paths=["data/1月.xlsx", "data/2月.xlsx", "data/3月.xlsx"],
    output_path="output/合併結果.xlsx",  # 可選，同時輸出
    add_source_column=True,              # 新增 _source_file 欄位標示來源
)
```

結果範例：

| 項目 | 金額 | _source_file |
|------|------|-------------|
| A | 100 | 1月.xlsx |
| B | 200 | 2月.xlsx |

### 5.2 合併同檔多個 Sheet

```python
handler = ExcelHandler("data/各部門.xlsx")

# 合併全部 Sheet
merged = handler.merge_sheets()

# 只合併指定 Sheet
merged = handler.merge_sheets(sheet_names=["製造部", "品保部"])
# 會有 _source_sheet 欄位
```

---

## 六、圖表生成

支援三種圖表類型：

| ChartType | 說明 |
|-----------|------|
| `ChartType.BAR` | 柱狀圖 |
| `ChartType.LINE` | 折線圖 |
| `ChartType.PIE` | 圓餅圖 |

```python
from openpyxl import Workbook
from app.utils.excel_styles import apply_style_to_range, StylePreset

wb = Workbook()
ws = wb.active

# 寫入資料（第 1 行表頭，第 2~6 行資料）
ws.append(["批次", "良率 (%)"])
for batch, rate in [("B1", 98), ("B2", 95), ("B3", 99), ("B4", 92), ("B5", 97)]:
    ws.append([batch, rate])

# 套用表頭樣式
apply_style_to_range(ws, 1, 1, 1, 2, StylePreset.HEADER)

# 新增柱狀圖
handler = ExcelHandler()
handler.add_chart(
    ws,
    chart_type=ChartType.BAR,
    data_range=(2, 1, 2, 6),         # 資料範圍 (min_col, min_row, max_col, max_row)
    categories_range=(1, 2, 1, 6),   # 分類軸範圍
    title="良率趨勢",
    position="D2",                   # 圖表放置位置
    x_axis_title="批次",
    y_axis_title="良率 (%)",
    width=15.0,                      # 圖表寬度（英吋）
    height=10.0,                     # 圖表高度（英吋）
)

wb.save("output/chart.xlsx")
```

**data_range 說明：** `(min_col, min_row, max_col, max_row)` 全部 1-based。  
例如 B1:B6 = `(2, 1, 2, 6)`，A2:A6 = `(1, 2, 1, 6)`。

---

## 七、樣式預設

內建 6 種樣式，可直接套用到儲存格：

| StylePreset | 外觀 | 用途 |
|-------------|------|------|
| `HEADER` | 藍底白字粗體、置中 | 表頭 |
| `DATA` | 標準字體、框線 | 一般資料 |
| `HIGHLIGHT` | 黃底粗體 | 重點標示 |
| `ERROR` | 紅字紅底 | 錯誤資料 |
| `SUCCESS` | 綠字綠底 | 通過標示 |
| `TOTAL` | 粗體、藍灰底、雙線框 | 合計列 |

```python
from app.utils.excel_styles import apply_style, apply_style_to_range, StylePreset

# 單一儲存格
apply_style(ws, row=5, col=3, preset=StylePreset.ERROR)

# 矩形範圍
apply_style_to_range(ws, start_row=1, start_col=1, end_row=1, end_col=5, preset=StylePreset.HEADER)
```

---

## 八、完整管線範例

最常見的使用模式：**讀取 → 偵測 → 對應 → 驗證 → 處理**

```python
from app.utils.excel_handler import ExcelHandler
from app.utils.excel_validation import ColumnRule, DataType

# 1. 讀取 Excel
handler = ExcelHandler("data/upload.xlsx")
df = handler.read_sheet()

# 2. 定義欄位規則
rules = [
    ColumnRule(
        name="board_name",
        aliases=["Board Name", "板子名稱"],
        data_type=DataType.STRING,
        required=True,
    ),
    ColumnRule(
        name="panel_id",
        aliases=["Panel ID", "面板編號"],
        data_type=DataType.STRING,
        required=True,
    ),
    ColumnRule(
        name="test_value",
        aliases=["Test Value", "測試值"],
        data_type=DataType.FLOAT,
        min_value=0,
        max_value=100,
    ),
]

# 3. 自動欄位對應
mapping = handler.auto_map_columns(rules, df=df)
print(f"對應結果：{mapping}")

# 4. 驗證
result = handler.validate(df, rules, column_mapping=mapping)
if not result.is_valid:
    print(f"驗證失敗：{result.error_count} 個錯誤")
    for err in result.errors:
        print(f"  第 {err.row} 行：{err.message}")
    raise ValueError("資料有誤，請修正後重新上傳")

# 5. 轉為 dict list → 可用於寫入 DB
records = handler.to_dict_list(df)
print(f"準備寫入 {len(records)} 筆資料")
```

---

## 九、FastAPI 整合範例

### 上傳 Excel 並驗證

```python
from fastapi import APIRouter, File, UploadFile, HTTPException
from app.utils.excel_handler import ExcelHandler
from app.utils.excel_validation import ColumnRule, DataType
from app.schemas.base import ApiResponse
import tempfile
import os

router = APIRouter(prefix="/excel", tags=["Excel"])

@router.post("/upload", response_model=ApiResponse)
async def upload_excel(file: UploadFile = File(...)):
    """上傳 Excel 並驗證資料。"""
    # 存到暫存檔
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        handler = ExcelHandler(tmp_path)
        df = handler.read_sheet()

        rules = [
            ColumnRule(name="board_name", aliases=["Board Name"], data_type=DataType.STRING, required=True),
            ColumnRule(name="value", aliases=["Test Value"], data_type=DataType.FLOAT, min_value=0),
        ]

        mapping = handler.auto_map_columns(rules, df=df)
        result = handler.validate(df, rules, column_mapping=mapping)

        if not result.is_valid:
            return ApiResponse(
                success=False,
                data={"errors": [e.__dict__ for e in result.errors[:50]]},
                message=f"驗證失敗：{result.error_count} 個錯誤",
            )

        records = handler.to_dict_list(df)
        return ApiResponse(
            data={"count": len(records), "preview": records[:5]},
            message="驗證通過",
        )
    finally:
        os.unlink(tmp_path)
```

### 匯出 Excel 下載

```python
from fastapi.responses import StreamingResponse

@router.get("/export")
async def export_excel():
    """匯出報表為 Excel 下載。"""
    data = [
        {"批次": "B001", "良率": 98.5, "不良數": 3},
        {"批次": "B002", "良率": 95.2, "不良數": 10},
    ]

    handler = ExcelHandler()
    buffer = handler.write(data=data, output_path=None, sheet_name="良率報表")

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=report.xlsx"},
    )
```

---

## API 速查表

| 方法 | 說明 | 回傳 |
|------|------|------|
| **讀取** | | |
| `read_sheet()` | 讀取單一 Sheet | `DataFrame` |
| `read_all_sheets()` | 讀取所有 Sheet | `Dict[str, DataFrame]` |
| `read_large_file()` | 串流逐批讀取 | `Iterator[DataFrame]` |
| `get_sheet_names()` | 取得 Sheet 名稱清單 | `List[str]` |
| `get_sheet_info()` | 取得 Sheet 基本資訊 | `List[Dict]` |
| **偵測** | | |
| `detect_columns()` | 偵測欄位型別與統計 | `List[Dict]` |
| `auto_map_columns()` | 用別名自動匹配欄位 | `Dict[str, str]` |
| **驗證** | | |
| `validate()` | 依規則驗證 DataFrame | `ValidationResult` |
| **寫入** | | |
| `write()` | 寫入美化 Excel | `Path \| BytesIO` |
| `write_multiple_sheets()` | 多 Sheet 寫入 | `Path \| BytesIO` |
| `add_chart()` | 新增圖表到工作表 | `None` |
| **合併** | | |
| `merge_files()` | 合併多個 Excel 檔 | `DataFrame` |
| `merge_sheets()` | 合併同檔多 Sheet | `DataFrame` |
| **工具** | | |
| `to_dict_list()` | DataFrame → List[Dict] | `List[Dict]` |
