from __future__ import annotations

"""
FileSearcher — 通用檔案 / 資料夾搜尋工具類別。

功能涵蓋：
- 搜尋：依檔名、副檔名、glob、正則、大小、日期範圍
- 篩選：串接多條件過濾（Builder 模式）
- 資訊：取得檔案詳細資訊、目錄樹狀結構
- 統計：依副檔名分類計數、目錄大小彙總
- 重複：依檔名或 hash 偵測重複檔案
- 批次：批次更名、搬移、複製、刪除（回傳預覽，需確認才執行）
"""

import fnmatch
import hashlib
import logging
import os
import re
import shutil
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)

logger = logging.getLogger(__name__)


class FileInfo:
    """單一檔案 / 資料夾的詳細資訊。"""

    __slots__ = (
        "path", "name", "stem", "suffix", "is_file", "is_dir",
        "size", "created_at", "modified_at", "accessed_at",
    )

    def __init__(self, path: Path) -> None:
        stat = path.stat()
        self.path: str = str(path)
        self.name: str = path.name
        self.stem: str = path.stem
        self.suffix: str = path.suffix.lower()
        self.is_file: bool = path.is_file()
        self.is_dir: bool = path.is_dir()
        self.size: int = stat.st_size
        self.created_at: datetime = datetime.fromtimestamp(stat.st_ctime)
        self.modified_at: datetime = datetime.fromtimestamp(stat.st_mtime)
        self.accessed_at: datetime = datetime.fromtimestamp(stat.st_atime)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "name": self.name,
            "stem": self.stem,
            "suffix": self.suffix,
            "is_file": self.is_file,
            "is_dir": self.is_dir,
            "size": self.size,
            "size_human": self._human_size(self.size),
            "created_at": self.created_at.isoformat(),
            "modified_at": self.modified_at.isoformat(),
            "accessed_at": self.accessed_at.isoformat(),
        }

    @staticmethod
    def _human_size(size: int) -> str:
        for unit in ("B", "KB", "MB", "GB", "TB"):
            if abs(size) < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0  # type: ignore[assignment]
        return f"{size:.1f} PB"


class FileSearcher:
    """
    通用檔案搜尋器。

    支援 Builder 模式串接條件：
        results = (
            FileSearcher("D:/data")
            .ext(".xlsx", ".csv")
            .name_contains("report")
            .size_between(min_kb=10)
            .modified_after(datetime(2024, 1, 1))
            .search()
        )

    Attributes:
        root: 搜尋的根目錄。
        recursive: 是否遞迴搜尋子目錄。
    """

    def __init__(
        self,
        root: Union[str, Path],
        recursive: bool = True,
    ) -> None:
        self.root: Path = Path(root).resolve()
        self.recursive: bool = recursive
        self._filters: List[Callable[[Path], bool]] = []
        self._include_files: bool = True
        self._include_dirs: bool = False
        self._max_depth: Optional[int] = None
        self._limit: Optional[int] = None

        if not self.root.exists():
            raise FileNotFoundError(f"根目錄不存在：{self.root}")
        if not self.root.is_dir():
            raise NotADirectoryError(f"路徑不是目錄：{self.root}")

    # ==================================================================
    # Builder 方法 — 條件設定（回傳 self 可串接）
    # ==================================================================

    def files_only(self) -> "FileSearcher":
        """只搜尋檔案（預設）。"""
        self._include_files = True
        self._include_dirs = False
        return self

    def dirs_only(self) -> "FileSearcher":
        """只搜尋資料夾。"""
        self._include_files = False
        self._include_dirs = True
        return self

    def files_and_dirs(self) -> "FileSearcher":
        """同時搜尋檔案與資料夾。"""
        self._include_files = True
        self._include_dirs = True
        return self

    def max_depth(self, depth: int) -> "FileSearcher":
        """限制遞迴深度（0 = 只看根目錄）。"""
        self._max_depth = depth
        return self

    def limit(self, n: int) -> "FileSearcher":
        """限制回傳數量。"""
        self._limit = n
        return self

    def ext(self, *extensions: str) -> "FileSearcher":
        """
        依副檔名篩選（不分大小寫）。

        用法：.ext(".xlsx", ".csv") 或 .ext("xlsx", "csv")
        """
        normalized: Set[str] = set()
        for e in extensions:
            e = e.strip().lower()
            if not e.startswith("."):
                e = "." + e
            normalized.add(e)

        self._filters.append(
            lambda p: p.suffix.lower() in normalized
        )
        return self

    def name_equals(self, name: str, case_sensitive: bool = False) -> "FileSearcher":
        """檔名完全比對。"""
        if case_sensitive:
            self._filters.append(lambda p: p.name == name)
        else:
            lower = name.lower()
            self._filters.append(lambda p: p.name.lower() == lower)
        return self

    def name_contains(self, keyword: str, case_sensitive: bool = False) -> "FileSearcher":
        """檔名包含關鍵字。"""
        if case_sensitive:
            self._filters.append(lambda p: keyword in p.name)
        else:
            lower = keyword.lower()
            self._filters.append(lambda p: lower in p.name.lower())
        return self

    def name_startswith(self, prefix: str, case_sensitive: bool = False) -> "FileSearcher":
        """檔名以指定字串開頭。"""
        if case_sensitive:
            self._filters.append(lambda p: p.name.startswith(prefix))
        else:
            lower = prefix.lower()
            self._filters.append(lambda p: p.name.lower().startswith(lower))
        return self

    def name_endswith(self, suffix: str, case_sensitive: bool = False) -> "FileSearcher":
        """檔名以指定字串結尾。"""
        if case_sensitive:
            self._filters.append(lambda p: p.name.endswith(suffix))
        else:
            lower = suffix.lower()
            self._filters.append(lambda p: p.name.lower().endswith(lower))
        return self

    def name_glob(self, pattern: str) -> "FileSearcher":
        """
        用 glob 模式比對檔名（如 ``report_*.xlsx``）。

        只比對檔名部分，不含路徑。
        """
        self._filters.append(
            lambda p: fnmatch.fnmatch(p.name.lower(), pattern.lower())
        )
        return self

    def name_regex(self, pattern: str, flags: int = re.IGNORECASE) -> "FileSearcher":
        """用正則表達式比對檔名。"""
        compiled = re.compile(pattern, flags)
        self._filters.append(lambda p: bool(compiled.search(p.name)))
        return self

    def path_contains(self, keyword: str, case_sensitive: bool = False) -> "FileSearcher":
        """完整路徑包含關鍵字。"""
        if case_sensitive:
            self._filters.append(lambda p: keyword in str(p))
        else:
            lower = keyword.lower()
            self._filters.append(lambda p: lower in str(p).lower())
        return self

    def size_between(
        self,
        min_bytes: Optional[int] = None,
        max_bytes: Optional[int] = None,
        min_kb: Optional[float] = None,
        max_kb: Optional[float] = None,
        min_mb: Optional[float] = None,
        max_mb: Optional[float] = None,
    ) -> "FileSearcher":
        """依檔案大小篩選。多種單位可混用，取最嚴格。"""
        lo: Optional[float] = None
        hi: Optional[float] = None

        for val, unit in [
            (min_bytes, 1), (min_kb, 1024), (min_mb, 1024 * 1024),
        ]:
            if val is not None:
                v = val * unit
                lo = v if lo is None else max(lo, v)

        for val, unit in [
            (max_bytes, 1), (max_kb, 1024), (max_mb, 1024 * 1024),
        ]:
            if val is not None:
                v = val * unit
                hi = v if hi is None else min(hi, v)

        def _filter(p: Path) -> bool:
            try:
                s = p.stat().st_size
            except OSError:
                return False
            if lo is not None and s < lo:
                return False
            if hi is not None and s > hi:
                return False
            return True

        self._filters.append(_filter)
        return self

    def modified_after(self, dt: datetime) -> "FileSearcher":
        """修改時間在指定日期之後。"""
        ts = dt.timestamp()
        self._filters.append(
            lambda p: p.stat().st_mtime >= ts
        )
        return self

    def modified_before(self, dt: datetime) -> "FileSearcher":
        """修改時間在指定日期之前。"""
        ts = dt.timestamp()
        self._filters.append(
            lambda p: p.stat().st_mtime <= ts
        )
        return self

    def modified_between(self, start: datetime, end: datetime) -> "FileSearcher":
        """修改時間在區間內。"""
        ts_start = start.timestamp()
        ts_end = end.timestamp()
        self._filters.append(
            lambda p: ts_start <= p.stat().st_mtime <= ts_end
        )
        return self

    def created_after(self, dt: datetime) -> "FileSearcher":
        """建立時間在指定日期之後。"""
        ts = dt.timestamp()
        self._filters.append(
            lambda p: p.stat().st_ctime >= ts
        )
        return self

    def created_before(self, dt: datetime) -> "FileSearcher":
        """建立時間在指定日期之前。"""
        ts = dt.timestamp()
        self._filters.append(
            lambda p: p.stat().st_ctime <= ts
        )
        return self

    def custom_filter(self, fn: Callable[[Path], bool]) -> "FileSearcher":
        """自訂篩選函式。"""
        self._filters.append(fn)
        return self

    def exclude_names(self, *names: str) -> "FileSearcher":
        """排除指定檔名 / 資料夾名。"""
        excluded = {n.lower() for n in names}
        self._filters.append(
            lambda p: p.name.lower() not in excluded
        )
        return self

    def exclude_patterns(self, *patterns: str) -> "FileSearcher":
        """排除符合 glob 模式的檔名。"""
        self._filters.append(
            lambda p: not any(
                fnmatch.fnmatch(p.name.lower(), pat.lower()) for pat in patterns
            )
        )
        return self

    def exclude_dirs(self, *dir_names: str) -> "FileSearcher":
        """排除指定資料夾（不進入該資料夾搜尋）。"""
        excluded = {n.lower() for n in dir_names}
        self._filters.append(
            lambda p: not any(
                part.lower() in excluded for part in p.relative_to(self.root).parts[:-1]
            )
        )
        return self

    # ==================================================================
    # 搜尋執行
    # ==================================================================

    def search(self) -> List[FileInfo]:
        """
        執行搜尋，回傳 FileInfo 清單。

        Returns:
            符合所有條件的 FileInfo 物件清單。
        """
        results: List[FileInfo] = []
        for path in self._walk():
            if self._limit is not None and len(results) >= self._limit:
                break
            results.append(FileInfo(path))

        logger.info("搜尋完成：%s 中找到 %d 個結果", self.root, len(results))
        return results

    def search_paths(self) -> List[Path]:
        """執行搜尋，只回傳 Path 清單（較輕量）。"""
        results: List[Path] = []
        for path in self._walk():
            if self._limit is not None and len(results) >= self._limit:
                break
            results.append(path)
        return results

    def search_names(self) -> List[str]:
        """執行搜尋，只回傳檔名清單。"""
        return [p.name for p in self.search_paths()]

    def iter_search(self) -> Iterator[FileInfo]:
        """
        惰性搜尋（Generator），適合大量檔案。

        Yields:
            逐一產生 FileInfo 物件。
        """
        count = 0
        for path in self._walk():
            if self._limit is not None and count >= self._limit:
                return
            yield FileInfo(path)
            count += 1

    def first(self) -> Optional[FileInfo]:
        """回傳第一個符合條件的結果，找不到回 None。"""
        for path in self._walk():
            return FileInfo(path)
        return None

    def count(self) -> int:
        """計算符合條件的數量（不載入 FileInfo）。"""
        return sum(1 for _ in self._walk())

    def exists(self) -> bool:
        """是否至少有一個符合條件的結果。"""
        return self.first() is not None

    # ==================================================================
    # 目錄資訊
    # ==================================================================

    def tree(
        self,
        max_depth: Optional[int] = None,
        show_size: bool = False,
        show_files: bool = True,
    ) -> str:
        """
        產生目錄樹狀結構字串。

        Args:
            max_depth: 最大深度。None 則不限。
            show_size: 是否顯示檔案大小。
            show_files: 是否顯示檔案（False 則只顯示資料夾）。

        Returns:
            樹狀結構字串。
        """
        lines: List[str] = [str(self.root)]
        self._build_tree(self.root, "", 0, max_depth, show_size, show_files, lines)
        return "\n".join(lines)

    def dir_summary(self) -> Dict[str, Any]:
        """
        回傳目錄摘要：總檔案數、總資料夾數、總大小、副檔名分佈。
        """
        file_count = 0
        dir_count = 0
        total_size = 0
        ext_stats: Dict[str, Dict[str, int]] = defaultdict(lambda: {"count": 0, "size": 0})

        for entry in self._iter_all_entries():
            if entry.is_file():
                file_count += 1
                size = entry.stat().st_size
                total_size += size
                suffix = entry.suffix.lower() or "(no ext)"
                ext_stats[suffix]["count"] += 1
                ext_stats[suffix]["size"] += size
            elif entry.is_dir():
                dir_count += 1

        # 排序：檔案數多到少
        sorted_ext = sorted(ext_stats.items(), key=lambda x: x[1]["count"], reverse=True)

        return {
            "root": str(self.root),
            "file_count": file_count,
            "dir_count": dir_count,
            "total_size": total_size,
            "total_size_human": FileInfo._human_size(total_size),
            "extensions": [
                {
                    "ext": ext,
                    "count": data["count"],
                    "size": data["size"],
                    "size_human": FileInfo._human_size(data["size"]),
                }
                for ext, data in sorted_ext
            ],
        }

    # ==================================================================
    # 重複檔偵測
    # ==================================================================

    def find_duplicates_by_name(self) -> Dict[str, List[str]]:
        """
        依檔名找重複檔案。

        Returns:
            {檔名: [路徑清單]}（只回傳有重複的）。
        """
        name_map: Dict[str, List[str]] = defaultdict(list)
        searcher = FileSearcher(self.root, recursive=self.recursive).files_only()
        for info in searcher.iter_search():
            name_map[info.name].append(info.path)

        return {k: v for k, v in name_map.items() if len(v) > 1}

    def find_duplicates_by_hash(
        self,
        algorithm: str = "md5",
        max_size_mb: float = 100,
    ) -> Dict[str, List[str]]:
        """
        依檔案內容 hash 找重複檔案。

        Args:
            algorithm: hash 演算法（md5, sha1, sha256）。
            max_size_mb: 超過此大小的檔案跳過（避免太慢）。

        Returns:
            {hash值: [路徑清單]}（只回傳有重複的）。
        """
        max_bytes = int(max_size_mb * 1024 * 1024)
        hash_map: Dict[str, List[str]] = defaultdict(list)

        # 先依大小分組，大小不同一定不重複
        size_map: Dict[int, List[Path]] = defaultdict(list)
        searcher = FileSearcher(self.root, recursive=self.recursive).files_only()
        for path in searcher.search_paths():
            try:
                size = path.stat().st_size
                if size <= max_bytes:
                    size_map[size].append(path)
            except OSError:
                continue

        # 只對大小相同的檔案計算 hash
        for size, paths in size_map.items():
            if len(paths) < 2:
                continue
            for path in paths:
                try:
                    h = self._file_hash(path, algorithm)
                    hash_map[h].append(str(path))
                except OSError:
                    continue

        return {k: v for k, v in hash_map.items() if len(v) > 1}

    # ==================================================================
    # 批次操作（預覽 + 執行）
    # ==================================================================

    def batch_preview(
        self,
        action: str,
        destination: Optional[Union[str, Path]] = None,
        rename_fn: Optional[Callable[[str], str]] = None,
    ) -> List[Dict[str, str]]:
        """
        預覽批次操作，不實際執行。

        Args:
            action: "copy" / "move" / "delete" / "rename"
            destination: copy / move 的目標資料夾。
            rename_fn: rename 時的命名函式，接收原檔名回傳新檔名。

        Returns:
            預覽清單 [{action, source, target}, ...]
        """
        paths = self.search_paths()
        previews: List[Dict[str, str]] = []

        for p in paths:
            entry: Dict[str, str] = {"action": action, "source": str(p)}

            if action == "delete":
                entry["target"] = "(刪除)"
            elif action in ("copy", "move"):
                if destination is None:
                    raise ValueError(f"{action} 需要指定 destination")
                dest = Path(destination) / p.name
                entry["target"] = str(dest)
            elif action == "rename":
                if rename_fn is None:
                    raise ValueError("rename 需要指定 rename_fn")
                new_name = rename_fn(p.name)
                entry["target"] = str(p.parent / new_name)
            else:
                raise ValueError(f"不支援的 action: {action}")

            previews.append(entry)

        return previews

    def batch_execute(
        self,
        action: str,
        destination: Optional[Union[str, Path]] = None,
        rename_fn: Optional[Callable[[str], str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        執行批次操作。

        回傳每筆操作的結果（含 success / error）。
        """
        paths = self.search_paths()
        results: List[Dict[str, Any]] = []

        if destination is not None:
            Path(destination).mkdir(parents=True, exist_ok=True)

        for p in paths:
            entry: Dict[str, Any] = {"action": action, "source": str(p)}
            try:
                if action == "delete":
                    if p.is_file():
                        p.unlink()
                    elif p.is_dir():
                        shutil.rmtree(str(p))
                    entry["success"] = True

                elif action == "copy":
                    if destination is None:
                        raise ValueError("copy 需要 destination")
                    dest = Path(destination) / p.name
                    if p.is_file():
                        shutil.copy2(str(p), str(dest))
                    else:
                        shutil.copytree(str(p), str(dest))
                    entry["target"] = str(dest)
                    entry["success"] = True

                elif action == "move":
                    if destination is None:
                        raise ValueError("move 需要 destination")
                    dest = Path(destination) / p.name
                    shutil.move(str(p), str(dest))
                    entry["target"] = str(dest)
                    entry["success"] = True

                elif action == "rename":
                    if rename_fn is None:
                        raise ValueError("rename 需要 rename_fn")
                    new_name = rename_fn(p.name)
                    new_path = p.parent / new_name
                    p.rename(new_path)
                    entry["target"] = str(new_path)
                    entry["success"] = True

                else:
                    raise ValueError(f"不支援的 action: {action}")

            except Exception as e:
                entry["success"] = False
                entry["error"] = str(e)

            results.append(entry)

        logger.info(
            "批次 %s 完成：%d 成功 / %d 失敗",
            action,
            sum(1 for r in results if r.get("success")),
            sum(1 for r in results if not r.get("success")),
        )
        return results

    # ==================================================================
    # 快捷靜態方法
    # ==================================================================

    @staticmethod
    def find_files(
        root: Union[str, Path],
        pattern: str = "*",
        recursive: bool = True,
    ) -> List[str]:
        """
        快速搜尋檔案（一行完成）。

        Args:
            root: 根目錄。
            pattern: glob 模式（如 ``*.xlsx``）。
            recursive: 是否遞迴。

        Returns:
            檔案路徑字串清單。
        """
        root_path = Path(root)
        if recursive:
            return [str(p) for p in root_path.rglob(pattern) if p.is_file()]
        return [str(p) for p in root_path.glob(pattern) if p.is_file()]

    @staticmethod
    def find_dirs(
        root: Union[str, Path],
        pattern: str = "*",
        recursive: bool = True,
    ) -> List[str]:
        """快速搜尋資料夾。"""
        root_path = Path(root)
        if recursive:
            return [str(p) for p in root_path.rglob(pattern) if p.is_dir()]
        return [str(p) for p in root_path.glob(pattern) if p.is_dir()]

    @staticmethod
    def get_file_info(path: Union[str, Path]) -> Dict[str, Any]:
        """取得單一檔案的詳細資訊。"""
        return FileInfo(Path(path)).to_dict()

    # ==================================================================
    # 內部方法
    # ==================================================================

    def _walk(self) -> Iterator[Path]:
        """核心遍歷方法，套用所有篩選條件。"""
        for entry in self._iter_entries(self.root, depth=0):
            if self._should_include(entry) and self._matches_filters(entry):
                yield entry

    def _iter_entries(self, directory: Path, depth: int) -> Iterator[Path]:
        """遞迴遍歷目錄。"""
        try:
            entries = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except PermissionError:
            logger.warning("權限不足，跳過：%s", directory)
            return
        except OSError as e:
            logger.warning("無法存取 %s：%s", directory, e)
            return

        for entry in entries:
            yield entry
            if (
                entry.is_dir()
                and self.recursive
                and (self._max_depth is None or depth < self._max_depth)
            ):
                yield from self._iter_entries(entry, depth + 1)

    def _iter_all_entries(self) -> Iterator[Path]:
        """遍歷所有檔案與資料夾（不套用篩選，用於統計）。"""
        yield from self._iter_entries(self.root, depth=0)

    def _should_include(self, path: Path) -> bool:
        """根據 include_files / include_dirs 決定是否納入。"""
        if path.is_file() and self._include_files:
            return True
        if path.is_dir() and self._include_dirs:
            return True
        return False

    def _matches_filters(self, path: Path) -> bool:
        """路徑是否通過所有篩選條件。"""
        return all(f(path) for f in self._filters)

    def _build_tree(
        self,
        directory: Path,
        prefix: str,
        depth: int,
        max_depth: Optional[int],
        show_size: bool,
        show_files: bool,
        lines: List[str],
    ) -> None:
        """遞迴建構樹狀結構。"""
        if max_depth is not None and depth >= max_depth:
            return

        try:
            entries = sorted(
                directory.iterdir(),
                key=lambda p: (not p.is_dir(), p.name.lower()),
            )
        except (PermissionError, OSError):
            return

        if not show_files:
            entries = [e for e in entries if e.is_dir()]

        for i, entry in enumerate(entries):
            is_last = i == len(entries) - 1
            connector = "└── " if is_last else "├── "
            size_str = ""
            if show_size and entry.is_file():
                size_str = f"  ({FileInfo._human_size(entry.stat().st_size)})"

            lines.append(f"{prefix}{connector}{entry.name}{size_str}")

            if entry.is_dir():
                extension = "    " if is_last else "│   "
                self._build_tree(
                    entry, prefix + extension,
                    depth + 1, max_depth, show_size, show_files, lines,
                )

    @staticmethod
    def _file_hash(path: Path, algorithm: str = "md5") -> str:
        """計算檔案 hash。"""
        h = hashlib.new(algorithm)
        with open(str(path), "rb") as f:
            while True:
                chunk = f.read(8192)
                if not chunk:
                    break
                h.update(chunk)
        return h.hexdigest()
