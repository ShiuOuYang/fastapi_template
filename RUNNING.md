# Quick Start (Windows)

## 1) 建立並啟用虛擬環境

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

## 2) 安裝依賴

```powershell
pip install -r requirements.txt
# 需要跑測試時
pip install -r requirements-dev.txt
```

## 3) 準備環境檔

```powershell
Copy-Item .env.example .env -Force
```

呼叫資料庫相關 API 之前，先在 `.env` 填好連線設定。
只想先看 API 文件的話，可以不填，服務仍會正常啟動。

## 4) 從專案根目錄啟動

Option A：

```powershell
python run.py
```

Option B：

```powershell
.\run.ps1
```

Option C（直接下指令）：

```powershell
python -m uvicorn app.main:app --app-dir src --host 0.0.0.0 --port 8000 --reload
```

## 5) 開啟 API 文件

- http://localhost:8000/docs
- http://localhost:8000/redoc

## 6) 執行測試

```powershell
pytest
```

## 備註

- 本專案採 src layout，啟動時需要把 `src` 加入模組搜尋路徑；
  三種啟動方式都已處理好，建議統一用 `python run.py`。
- `src\app\main.py` 也支援直接執行，但仍以根目錄啟動為主要流程。
- 本機想讓 SQLAlchemy 自動建表，把 `.env` 的 `DB_AUTO_CREATE` 設為 `true`。
