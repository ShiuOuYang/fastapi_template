from __future__ import annotations

"""檔案搜尋相關 API — 瀏覽、搜尋、統計、樹狀結構、重複偵測。"""

import asyncio
import functools
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.schemas.base import ApiResponse
from app.utils.file_searcher import FileSearcher

router = APIRouter(prefix="/files", tags=["File Search"])

# 預設搜尋根目錄；實務上可改為從設定檔或參數取得
DEFAULT_ROOT = Path(__file__).resolve().parents[4]


def _run_sync(func, *args, **kwargs):  # type: ignore[no-untyped-def]
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(None, functools.partial(func, *args, **kwargs))


def _safe_root(root: Optional[str]) -> Path:
    """驗證並回傳安全的根目錄路徑。"""
    if root is None:
        return DEFAULT_ROOT
    p = Path(root).resolve()
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"路徑不存在：{root}")
    if not p.is_dir():
        raise HTTPException(status_code=400, detail=f"路徑不是目錄：{root}")
    return p


# ======================================================================
# 1. 目錄瀏覽（列出檔案與資料夾）
# ======================================================================

@router.get("/browse", response_model=ApiResponse)
async def browse_directory(
    root: Optional[str] = Query(default=None, description="目錄路徑，不填則使用專案根目錄"),
    show_hidden: bool = Query(default=False, description="是否顯示隱藏檔"),
) -> ApiResponse:
    """瀏覽指定目錄下的檔案與資料夾（不遞迴）。"""
    base = _safe_root(root)

    def _browse() -> List[Dict[str, Any]]:
        searcher = FileSearcher(base, recursive=False).files_and_dirs()
        if not show_hidden:
            searcher.exclude_patterns(".*")
        results = searcher.search()
        return [r.to_dict() for r in results]

    items = await _run_sync(_browse)

    dirs = [i for i in items if i["is_dir"]]
    files = [i for i in items if i["is_file"]]

    return ApiResponse(
        data={"path": str(base), "dirs": dirs, "files": files},
        message=f"{len(dirs)} 個資料夾，{len(files)} 個檔案",
    )


# ======================================================================
# 2. 搜尋檔案
# ======================================================================

@router.get("/search", response_model=ApiResponse)
async def search_files(
    root: Optional[str] = Query(default=None, description="搜尋根目錄"),
    keyword: Optional[str] = Query(default=None, description="檔名關鍵字"),
    ext: Optional[str] = Query(default=None, description="副檔名（逗號分隔，如 .xlsx,.csv）"),
    glob: Optional[str] = Query(default=None, description="glob 模式（如 report_*.xlsx）"),
    regex: Optional[str] = Query(default=None, description="正則表達式"),
    min_size_kb: Optional[float] = Query(default=None, ge=0, description="最小檔案大小 (KB)"),
    max_size_mb: Optional[float] = Query(default=None, ge=0, description="最大檔案大小 (MB)"),
    recursive: bool = Query(default=True, description="是否遞迴搜尋子目錄"),
    limit: int = Query(default=200, ge=1, le=5000, description="回傳數量上限"),
) -> ApiResponse:
    """
    多條件搜尋檔案。所有條件為 AND 關係。

    範例：
    - `/api/v1/files/search?keyword=report&ext=.xlsx`
    - `/api/v1/files/search?glob=*.py&recursive=true`
    - `/api/v1/files/search?min_size_kb=100&max_size_mb=10`
    """
    base = _safe_root(root)

    def _search() -> List[Dict[str, Any]]:
        searcher = FileSearcher(base, recursive=recursive).files_only().limit(limit)

        if keyword:
            searcher.name_contains(keyword)
        if ext:
            extensions = [e.strip() for e in ext.split(",")]
            searcher.ext(*extensions)
        if glob:
            searcher.name_glob(glob)
        if regex:
            searcher.name_regex(regex)
        if min_size_kb is not None or max_size_mb is not None:
            searcher.size_between(min_kb=min_size_kb, max_mb=max_size_mb)

        # 排除常見不需要搜尋的目錄
        searcher.exclude_dirs("__pycache__", ".git", "node_modules", "venv", ".venv")

        return [r.to_dict() for r in searcher.search()]

    results = await _run_sync(_search)

    return ApiResponse(
        data={"total": len(results), "results": results},
        message=f"找到 {len(results)} 個檔案",
    )


# ======================================================================
# 3. 目錄樹狀結構
# ======================================================================

@router.get("/tree", response_model=ApiResponse)
async def directory_tree(
    root: Optional[str] = Query(default=None, description="目錄路徑"),
    max_depth: int = Query(default=3, ge=1, le=10, description="最大深度"),
    show_size: bool = Query(default=False, description="是否顯示檔案大小"),
    show_files: bool = Query(default=True, description="是否顯示檔案（False 只顯示資料夾）"),
) -> ApiResponse:
    """產生目錄樹狀結構。"""
    base = _safe_root(root)

    def _tree() -> str:
        searcher = FileSearcher(base)
        return searcher.tree(max_depth=max_depth, show_size=show_size, show_files=show_files)

    tree_str = await _run_sync(_tree)
    line_count = tree_str.count("\n") + 1

    return ApiResponse(
        data={"tree": tree_str, "lines": line_count},
        message=f"樹狀結構共 {line_count} 行",
    )


# ======================================================================
# 4. 目錄統計摘要
# ======================================================================

@router.get("/stats", response_model=ApiResponse)
async def directory_stats(
    root: Optional[str] = Query(default=None, description="目錄路徑"),
) -> ApiResponse:
    """取得目錄統計：檔案數、資料夾數、總大小、副檔名分佈。"""
    base = _safe_root(root)

    def _stats() -> Dict[str, Any]:
        searcher = FileSearcher(base)
        return searcher.dir_summary()

    summary = await _run_sync(_stats)

    return ApiResponse(data=summary, message=f"共 {summary['file_count']} 個檔案")


# ======================================================================
# 5. 單一檔案資訊
# ======================================================================

@router.get("/info", response_model=ApiResponse)
async def file_info(
    path: str = Query(..., description="檔案或資料夾的完整路徑"),
) -> ApiResponse:
    """取得單一檔案或資料夾的詳細資訊。"""
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail=f"路徑不存在：{path}")

    info = await _run_sync(FileSearcher.get_file_info, path)
    return ApiResponse(data=info)


# ======================================================================
# 6. 搜尋重複檔案
# ======================================================================

@router.get("/duplicates", response_model=ApiResponse)
async def find_duplicates(
    root: Optional[str] = Query(default=None, description="搜尋根目錄"),
    method: str = Query(default="name", description="比對方式：name（檔名）或 hash（內容）"),
    max_size_mb: float = Query(default=100, ge=1, description="hash 模式下跳過超過此大小的檔案 (MB)"),
) -> ApiResponse:
    """偵測重複檔案，依檔名或內容 hash 比對。"""
    base = _safe_root(root)

    def _duplicates() -> Dict[str, List[str]]:
        searcher = FileSearcher(base)
        if method == "hash":
            return searcher.find_duplicates_by_hash(max_size_mb=max_size_mb)
        return searcher.find_duplicates_by_name()

    result = await _run_sync(_duplicates)
    total_groups = len(result)
    total_files = sum(len(v) for v in result.values())

    return ApiResponse(
        data={"method": method, "groups": total_groups, "duplicates": result},
        message=f"找到 {total_groups} 組重複（共 {total_files} 個檔案）" if total_groups > 0 else "沒有重複檔案",
    )


# ======================================================================
# 7. 依副檔名分類統計
# ======================================================================

@router.get("/extensions", response_model=ApiResponse)
async def extension_stats(
    root: Optional[str] = Query(default=None, description="搜尋根目錄"),
    ext: Optional[str] = Query(default=None, description="只看指定副檔名（逗號分隔）"),
) -> ApiResponse:
    """列出各副檔名的檔案數量與大小。"""
    base = _safe_root(root)

    def _ext_stats() -> Dict[str, Any]:
        summary = FileSearcher(base).dir_summary()
        extensions = summary["extensions"]
        if ext:
            targets = {e.strip().lower() for e in ext.split(",")}
            targets = {e if e.startswith(".") else f".{e}" for e in targets}
            extensions = [e for e in extensions if e["ext"] in targets]
        return {
            "total_types": len(extensions),
            "extensions": extensions,
        }

    result = await _run_sync(_ext_stats)

    return ApiResponse(data=result, message=f"共 {result['total_types']} 種副檔名")
