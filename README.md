# FastAPI Template

一個乾淨、分層清楚的 FastAPI 後端模板。
clone 下來改個名字就能直接開始寫業務邏輯。

## 技術棧

- **Python** 3.8（公司環境標準；依賴版本上限已對齊 3.8，程式碼勿使用 3.9+ 語法）
- **FastAPI** + Uvicorn
- **SQLAlchemy 2.0**（async）+ SQL Server
- **aioodbc** + pyodbc（ODBC Driver 18 for SQL Server）
- **Pydantic v2** 資料驗證
- **pydantic-settings** 環境變數管理

## 專案結構

```
src/
  app/
    api/
      deps.py              # 共用依賴（SessionDep 等）
      v1/routes/
        item.py            # 範例 CRUD 路由
    core/
      config.py            # 環境設定（從 .env 載入）
      database.py          # engine / AsyncSession factory / 交易邊界
    models/                # SQLAlchemy ORM models
    schemas/
      base.py              # ApiResponse、Page 等共用 schema
      item.py              # 範例 request / response schema
    repositories/
      base.py              # 泛型 CRUD 基底類別
      item.py              # 範例資料存取層
    services/              # 商業邏輯層
    main.py                # FastAPI 應用程式入口
tests/                     # pytest 測試
run.py / run.ps1           # 啟動腳本（run.ps1 會優先使用 venv 的 Python）
```

## 分層原則

| 層 | 職責 | 不該做的事 |
|----|------|-----------|
| `routes` | 解析 HTTP、驗證輸入、組 `ApiResponse` | 寫 SQL、寫業務判斷 |
| `services` | 業務流程與規則 | 直接碰 `session.execute` |
| `repositories` | 查詢與寫入（只 flush） | 呼叫 commit、做業務判斷 |
| `models` | 資料表結構 | 任何邏輯 |
| `schemas` | 對外資料契約 | 依賴 ORM 物件 |

交易邊界統一在 `core/database.py` 的 `get_session`：request 正常結束就 commit，
拋例外就 rollback。所以下層一律只 flush，不要自己 commit。

## 快速開始

### 1. 環境準備

```bash
# 安裝 ODBC Driver 18 for SQL Server
# Windows: 從 Microsoft 官網下載安裝
# Linux:   https://learn.microsoft.com/zh-tw/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server

python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

pip install -r requirements.txt
# 要跑測試的話：pip install -r requirements-dev.txt
```

### 2. 設定環境變數

```bash
copy .env.example .env   # Windows
# cp .env.example .env   # Linux/macOS
```

編輯 `.env` 填入資料庫連線資訊與應用名稱。

### 3. 資料庫

預設 **不會** 自動建表，資料表結構交由 DBA 或 migration 工具管理。
本機想快速起步時，把 `.env` 的 `DB_AUTO_CREATE` 設為 `true`，
啟動時就會依 model 建表。

### 4. 啟動服務

```bash
python run.py                 # 建議做法，從專案根目錄啟動
```

```powershell
.\run.ps1                     # PowerShell，可加 -Port 9000、-NoReload
```

```bash
python -m uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

### 5. API 文件

- Swagger UI：http://localhost:8000/docs
- ReDoc：http://localhost:8000/redoc

### 6. 執行測試

```bash
pytest
```

內建的測試不需要真實資料庫，但仍需安裝 ODBC driver manager
（Windows 內建；Linux 需 `unixodbc`，macOS 需 `brew install unixodbc`）。

## 統一回應格式

所有端點都回傳同一個外殼：

```json
{
  "success": true,
  "data": null,
  "message": ""
}
```

錯誤（含 404、422、未捕捉例外）也走同一格式，由 `main.py` 的全域例外處理器產生。
清單型端點的 `data` 會是分頁結構：

```json
{
  "success": true,
  "data": { "items": [], "total": 0, "skip": 0, "limit": 50 },
  "message": ""
}
```

## 內建端點

| 模組 | 路徑 | 說明 |
|------|------|------|
| Health | `GET /` | 健康檢查 |
| Item | `/api/v1/items` | 範例 CRUD（GET / POST / PATCH / DELETE） |

## 新增一個模組

以 `Item` 為樣板，依序建立五個檔案再註冊路由：

1. `models/<name>.py` — 定義資料表
2. `schemas/<name>.py` — 定義 Create / Update / Response
3. `repositories/<name>.py` — 繼承 `BaseRepository[Model]`，基本 CRUD 免寫
4. `services/<name>.py` — 業務邏輯
5. `api/v1/routes/<name>.py` — 路由與依賴注入
6. 在 `main.py` 加一行 `app.include_router(...)`，並在 `models/__init__.py` 匯出 model

## 拿掉範例模組

`Item` 只是分層寫法示範。不需要時刪掉這幾個檔案即可：

```
src/app/models/item.py
src/app/schemas/item.py
src/app/repositories/item.py
src/app/services/item.py
src/app/api/v1/routes/item.py
```

再清掉 `models/__init__.py` 的匯出、`main.py` 的 `include_router`，
以及 `tests/test_health.py` 裡對 `/api/v1/items` 的斷言。

## 連線字串格式

```
mssql+aioodbc://{user}:{password}@{host}:{port}/{dbname}?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```
