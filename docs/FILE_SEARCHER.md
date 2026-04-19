# FileSearcher 使用說明

通用檔案 / 資料夾搜尋工具，支援 Builder 模式串接多條件搜尋。

---

## 目錄

1. [快速開始](#1-快速開始)
2. [Builder 搜尋條件](#2-builder-搜尋條件)
3. [執行搜尋](#3-執行搜尋)
4. [目錄資訊](#4-目錄資訊)
5. [重複檔偵測](#5-重複檔偵測)
6. [批次操作](#6-批次操作)
7. [快捷方法](#7-快捷方法)
8. [API 端點](#8-api-端點)
9. [完整範例](#9-完整範例)

---

## 1. 快速開始

```python
from app.utils.file_searcher import FileSearcher

# 最簡單的用法：搜尋目錄下所有檔案
results = FileSearcher("D:/data").search()

for f in results:
    print(f"{f.name}  {f.size}  {f.modified_at}")
```

`search()` 回傳的是 `FileInfo` 物件清單，每個 `FileInfo` 包含：

| 屬性 | 型別 | 說明 |
|------|------|------|
| `path` | `str` | 完整路徑 |
| `name` | `str` | 檔案名稱（含副檔名） |
| `stem` | `str` | 不含副檔名的名稱 |
| `suffix` | `str` | 副檔名（小寫，含 `.`） |
| `is_file` | `bool` | 是否為檔案 |
| `is_dir` | `bool` | 是否為資料夾 |
| `size` | `int` | 大小（bytes） |
| `created_at` | `datetime` | 建立時間 |
| `modified_at` | `datetime` | 修改時間 |
| `accessed_at` | `datetime` | 存取時間 |

```python
# 轉成 dict
info_dict = results[0].to_dict()
# 自動計算人類可讀大小：size_human = "1.2 MB"
```

---

## 2. Builder 搜尋條件

所有條件方法都回傳 `self`，可以 **鏈式串接**，條件之間是 **AND** 關係。

### 2.1 檔案 / 資料夾篩選

```python
FileSearcher("D:/data").files_only()       # 只找檔案（預設）
FileSearcher("D:/data").dirs_only()         # 只找資料夾
FileSearcher("D:/data").files_and_dirs()    # 兩種都找
```

### 2.2 副檔名

```python
# 可帶或不帶 "."，不分大小寫
FileSearcher("D:/data").ext(".xlsx", ".csv")
FileSearcher("D:/data").ext("py", "js")
```

### 2.3 檔名比對

```python
# 完全比對
.name_equals("config.yaml")

# 包含關鍵字
.name_contains("report")

# 開頭 / 結尾
.name_startswith("test_")
.name_endswith("_backup")

# Glob 模式（只比對檔名）
.name_glob("report_*.xlsx")
.name_glob("*_2024*")

# 正則表達式
.name_regex(r"^report_\d{4}")
.name_regex(r"v\d+\.\d+", flags=0)  # 區分大小寫
```

### 2.4 路徑比對

```python
# 完整路徑包含關鍵字
.path_contains("backup")
.path_contains("2024/Q1")
```

### 2.5 檔案大小

```python
# 多種單位可混用
.size_between(min_kb=10)              # >= 10 KB
.size_between(max_mb=50)              # <= 50 MB
.size_between(min_kb=100, max_mb=10)  # 100KB ~ 10MB
.size_between(min_bytes=0, max_bytes=1024)
```

### 2.6 時間範圍

```python
from datetime import datetime

# 修改時間
.modified_after(datetime(2024, 1, 1))
.modified_before(datetime(2024, 12, 31))
.modified_between(datetime(2024, 1, 1), datetime(2024, 6, 30))

# 建立時間
.created_after(datetime(2024, 1, 1))
.created_before(datetime(2024, 12, 31))
```

### 2.7 排除

```python
# 排除特定檔名
.exclude_names("thumbs.db", ".DS_Store")

# 排除符合模式的檔名
.exclude_patterns("*.tmp", "*.log", "~*")

# 排除特定資料夾（不會進入搜尋）
.exclude_dirs("__pycache__", ".git", "node_modules", "venv")
```

### 2.8 深度與數量

```python
.max_depth(2)   # 只搜尋到第 2 層（0 = 只看根目錄）
.limit(100)     # 最多回傳 100 筆
```

### 2.9 自訂篩選

```python
# 傳入一個函式，接收 Path 回傳 bool
.custom_filter(lambda p: p.stat().st_size % 2 == 0)

# 更實用的例子：只找非空檔案
.custom_filter(lambda p: p.stat().st_size > 0)
```

---

## 3. 執行搜尋

設定完條件後，有多種方式取得結果：

```python
searcher = FileSearcher("D:/data").ext(".xlsx").name_contains("report")

# 1. 取得 FileInfo 清單
results = searcher.search()

# 2. 只取 Path 清單（較輕量）
paths = searcher.search_paths()

# 3. 只取檔名清單
names = searcher.search_names()
# ["report_2024.xlsx", "report_2025.xlsx"]

# 4. 惰性搜尋（大量檔案時用 Generator 逐一產生）
for info in searcher.iter_search():
    print(info.name)

# 5. 取第一個結果
first = searcher.first()  # FileInfo 或 None

# 6. 計算數量（不載入詳細資訊）
total = searcher.count()

# 7. 是否存在
has_result = searcher.exists()  # True / False
```

---

## 4. 目錄資訊

### 4.1 樹狀結構

```python
searcher = FileSearcher("D:/project")
tree = searcher.tree(max_depth=3, show_size=True, show_files=True)
print(tree)
```

輸出：
```
D:\project
├── src
│   ├── app
│   │   ├── main.py  (3.2 KB)
│   │   └── config.py  (1.1 KB)
│   └── tests
│       └── test_main.py  (0.8 KB)
├── README.md  (2.5 KB)
└── requirements.txt  (0.3 KB)
```

參數：
- `max_depth`：最大深度，`None` 不限
- `show_size`：是否顯示檔案大小
- `show_files`：`False` 只顯示資料夾結構

### 4.2 目錄統計摘要

```python
summary = FileSearcher("D:/project").dir_summary()
```

回傳：
```json
{
    "root": "D:\\project",
    "file_count": 122,
    "dir_count": 21,
    "total_size": 424008,
    "total_size_human": "414.1 KB",
    "extensions": [
        {"ext": ".py", "count": 39, "size": 136703, "size_human": "133.5 KB"},
        {"ext": ".xlsx", "count": 9, "size": 50312, "size_human": "49.1 KB"}
    ]
}
```

---

## 5. 重複檔偵測

### 5.1 依檔名找重複

```python
searcher = FileSearcher("D:/data")
duplicates = searcher.find_duplicates_by_name()

# 回傳：{"report.xlsx": ["D:/data/a/report.xlsx", "D:/data/b/report.xlsx"]}
for name, paths in duplicates.items():
    print(f"{name} 出現 {len(paths)} 次：")
    for p in paths:
        print(f"  - {p}")
```

### 5.2 依內容 hash 找重複

```python
# 即使檔名不同，內容相同也會偵測到
duplicates = searcher.find_duplicates_by_hash(
    algorithm="md5",       # 可選 md5, sha1, sha256
    max_size_mb=100,       # 跳過超過 100MB 的檔案
)

# 回傳：{"a1b2c3...": ["D:/data/file1.xlsx", "D:/data/copy_of_file1.xlsx"]}
```

---

## 6. 批次操作

### 6.1 預覽（不實際執行）

```python
searcher = FileSearcher("D:/old_data").ext(".tmp").modified_before(datetime(2023, 1, 1))

# 先預覽要做什麼
preview = searcher.batch_preview(action="delete")
for item in preview:
    print(f"{item['action']}: {item['source']} → {item['target']}")
```

### 6.2 複製

```python
preview = searcher.batch_preview(action="copy", destination="D:/backup")
# 確認沒問題後執行
results = searcher.batch_execute(action="copy", destination="D:/backup")
```

### 6.3 搬移

```python
results = searcher.batch_execute(action="move", destination="D:/archive")
```

### 6.4 批次更名

```python
# 用函式定義新檔名
def add_prefix(name: str) -> str:
    return f"backup_{name}"

preview = searcher.batch_preview(action="rename", rename_fn=add_prefix)
results = searcher.batch_execute(action="rename", rename_fn=add_prefix)

# 每筆結果包含 success / error
for r in results:
    if r["success"]:
        print(f"✓ {r['source']} → {r['target']}")
    else:
        print(f"✗ {r['source']}：{r['error']}")
```

---

## 7. 快捷方法

不需要建構 `FileSearcher` 物件，一行搞定：

```python
from app.utils.file_searcher import FileSearcher

# 搜尋所有 .xlsx 檔案
files = FileSearcher.find_files("D:/data", pattern="*.xlsx")
# ["D:/data/report.xlsx", "D:/data/sub/data.xlsx"]

# 搜尋所有資料夾
dirs = FileSearcher.find_dirs("D:/data", pattern="*backup*")

# 取得單一檔案資訊
info = FileSearcher.get_file_info("D:/data/report.xlsx")
# {"path": "...", "name": "report.xlsx", "size": 12345, "size_human": "12.1 KB", ...}
```

---

## 8. API 端點

所有 API 路徑前綴為 `/api/v1/files`，可在 `http://127.0.0.1:8000/docs` 查看互動式文件。

### 8.1 瀏覽目錄

```
GET /api/v1/files/browse?root=D:/data&show_hidden=false
```

回傳該目錄下的檔案與資料夾清單（不遞迴）。

### 8.2 多條件搜尋

```
GET /api/v1/files/search?keyword=report&ext=.xlsx,.csv&recursive=true&limit=200
```

| 參數 | 說明 | 預設 |
|------|------|------|
| `root` | 搜尋根目錄 | 專案根目錄 |
| `keyword` | 檔名包含的關鍵字 | — |
| `ext` | 副檔名，逗號分隔 | — |
| `glob` | glob 模式 | — |
| `regex` | 正則表達式 | — |
| `min_size_kb` | 最小檔案大小 (KB) | — |
| `max_size_mb` | 最大檔案大小 (MB) | — |
| `recursive` | 是否遞迴子目錄 | `true` |
| `limit` | 回傳上限 | `200` |

### 8.3 目錄樹狀結構

```
GET /api/v1/files/tree?max_depth=3&show_size=true&show_files=true
```

### 8.4 目錄統計

```
GET /api/v1/files/stats?root=D:/data
```

回傳檔案數、資料夾數、總大小、副檔名分佈。

### 8.5 單一檔案資訊

```
GET /api/v1/files/info?path=D:/data/report.xlsx
```

### 8.6 重複檔偵測

```
GET /api/v1/files/duplicates?method=name
GET /api/v1/files/duplicates?method=hash&max_size_mb=100
```

### 8.7 副檔名統計

```
GET /api/v1/files/extensions?ext=.py,.xlsx
```

---

## 9. 完整範例

### 範例 1：找出專案中所有大於 1MB 的圖片

```python
images = (
    FileSearcher("D:/project")
    .ext(".png", ".jpg", ".jpeg", ".gif", ".bmp")
    .size_between(min_mb=1)
    .exclude_dirs("node_modules", ".git")
    .search()
)

print(f"找到 {len(images)} 個大圖片：")
for img in images:
    print(f"  {img.name} ({img.to_dict()['size_human']})")
```

### 範例 2：找 2024 年修改過的 Excel 報表

```python
from datetime import datetime

reports = (
    FileSearcher("D:/reports")
    .ext(".xlsx")
    .name_contains("月報")
    .modified_between(datetime(2024, 1, 1), datetime(2024, 12, 31))
    .search()
)
```

### 範例 3：清理暫存檔

```python
searcher = (
    FileSearcher("D:/temp")
    .ext(".tmp", ".log", ".bak")
    .modified_before(datetime(2023, 1, 1))
)

# 先預覽
preview = searcher.batch_preview(action="delete")
print(f"即將刪除 {len(preview)} 個檔案")
for p in preview[:5]:
    print(f"  {p['source']}")

# 確認後執行
# results = searcher.batch_execute(action="delete")
```

### 範例 4：批次加前綴更名

```python
import re

def add_date_prefix(name: str) -> str:
    return f"2024_{name}"

searcher = FileSearcher("D:/data").ext(".csv").name_glob("sales_*")
preview = searcher.batch_preview(action="rename", rename_fn=add_date_prefix)

for p in preview:
    print(f"{p['source']} → {p['target']}")

# results = searcher.batch_execute(action="rename", rename_fn=add_date_prefix)
```

### 範例 5：搭配 ExcelHandler 使用

```python
from app.utils.file_searcher import FileSearcher
from app.utils.excel_handler import ExcelHandler

# 找出所有 Excel 檔
excel_files = FileSearcher("D:/data").ext(".xlsx").search_paths()

# 合併全部
handler = ExcelHandler()
merged = handler.merge_files(excel_files, output_path="D:/output/merged.xlsx")
print(f"合併了 {len(excel_files)} 個檔案，共 {len(merged)} 行")
```

### 範例 6：在 FastAPI 中結合使用

```python
from fastapi import APIRouter, Query
from app.utils.file_searcher import FileSearcher

router = APIRouter()

@router.get("/find-reports")
async def find_reports(year: int = Query(...)):
    from datetime import datetime
    results = (
        FileSearcher("D:/reports")
        .ext(".xlsx")
        .modified_between(datetime(year, 1, 1), datetime(year, 12, 31))
        .search()
    )
    return {"count": len(results), "files": [r.to_dict() for r in results]}
```
