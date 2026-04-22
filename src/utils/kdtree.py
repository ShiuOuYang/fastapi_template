"""
KD-Tree (K-Dimensional Tree) 實現與教學

KD-Tree 是一種二進制搜索樹的變體，用於在 K 維空間中組織點。
主要應用場景：
  1. 最近鄰搜索（Nearest Neighbor Search）
  2. 範圍搜索（Range Search）
  3. 空間索引
"""

from typing import List, Tuple, Optional
import math


class Point:
    """表示 K 維空間中的一個點"""
    
    def __init__(self, coordinates: List[float], name: str = None):
        """
        初始化一個點
        
        Args:
            coordinates: 坐標列表，例如 [x, y] 代表二維點
            name: 點的名稱（可選）
        """
        self.coordinates = coordinates
        self.name = name or f"P{id(self)}"
        self.k = len(coordinates)  # 維度數
    
    def distance_to(self, other: 'Point') -> float:
        """計算到另一個點的歐幾里得距離"""
        if self.k != other.k:
            raise ValueError(f"維度不相同: {self.k} vs {other.k}")
        
        return math.sqrt(
            sum((a - b) ** 2 for a, b in zip(self.coordinates, other.coordinates))
        )
    
    def __str__(self):
        return f"{self.name}{tuple(self.coordinates)}"
    
    def __repr__(self):
        return str(self)


class KDNode:
    """KD-Tree 的節點"""
    
    def __init__(self, point: Point, depth: int = 0):
        self.point = point
        self.depth = depth  # 節點的深度（用於決定分割軸）
        self.left = None
        self.right = None


class KDTree:
    """
    KD-Tree 的實現
    
    原理：
    ------
    1. 在每一層按照不同的維度來分割空間
    2. 第一層按照第 0 維(x軸)分割，第二層按照第 1 維(y軸)分割，以此類推
    3. 所有坐標小於當前點的坐標放在左子樹，大於等於的放在右子樹
    
    時間複雜度：
    ------
    - 構建: O(n log n)
    - 查詢（最壞情況）: O(n)
    - 查詢（平均情況）: O(log n)
    """
    
    def __init__(self, points: List[Point] = None):
        self.root = None
        self.k = None  # 維度數
        
        if points:
            if not points:
                raise ValueError("點列表不能為空")
            self.k = points[0].k
            self._build_tree(points)
    
    def _build_tree(self, points: List[Point]) -> KDNode:
        """
        遞歸構建 KD-Tree
        
        Args:
            points: 點的列表
        
        Returns:
            樹的根節點
        """
        if not points:
            return None
        
        # 計算深度，用於決定分割軸
        depth = 0 if self.root is None else 0
        
        def build_recursive(point_list: List[Point], depth: int) -> KDNode:
            if not point_list:
                return None
            
            # 決定在哪一維進行分割
            axis = depth % self.k
            
            # 按照該維度的坐標進行排序
            sorted_points = sorted(
                point_list,
                key=lambda p: p.coordinates[axis]
            )
            
            # 選擇中位數作為當前節點
            median_idx = len(sorted_points) // 2
            
            # 創建節點，並遞歸構建左右子樹
            node = KDNode(sorted_points[median_idx], depth)
            node.left = build_recursive(sorted_points[:median_idx], depth + 1)
            node.right = build_recursive(sorted_points[median_idx + 1:], depth + 1)
            
            return node
        
        self.root = build_recursive(points, 0)
        return self.root
    
    def insert(self, point: Point) -> None:
        """
        插入一個新的點
        
        Args:
            point: 要插入的點
        """
        if self.k is None:
            self.k = point.k
            self.root = KDNode(point, 0)
        else:
            if point.k != self.k:
                raise ValueError(f"維度不相同: {point.k} vs {self.k}")
            self._insert_recursive(self.root, point, 0)
    
    def _insert_recursive(self, node: KDNode, point: Point, depth: int) -> KDNode:
        """遞歸插入"""
        if node is None:
            return KDNode(point, depth)
        
        axis = depth % self.k
        
        if point.coordinates[axis] < node.point.coordinates[axis]:
            node.left = self._insert_recursive(node.left, point, depth + 1)
        else:
            node.right = self._insert_recursive(node.right, point, depth + 1)
        
        return node
    
    def find_nearest(self, target: Point) -> Tuple[Point, float]:
        """
        找到距離目標最近的點
        
        Args:
            target: 目標點
        
        Returns:
            (最近的點, 距離)
        """
        if self.root is None:
            return None, float('inf')
        
        best = [None, float('inf')]  # [最近點, 距離]
        
        def search_recursive(node: KDNode, depth: int) -> None:
            if node is None:
                return
            
            # 計算當前節點到目標的距離
            distance = target.distance_to(node.point)
            
            # 更新最近點
            if distance < best[1]:
                best[0] = node.point
                best[1] = distance
            
            # 決定分割軸
            axis = depth % self.k
            diff = target.coordinates[axis] - node.point.coordinates[axis]
            
            # 先搜索較近的一側
            near_child = node.left if diff < 0 else node.right
            far_child = node.right if diff < 0 else node.left
            
            search_recursive(near_child, depth + 1)
            
            # 只有當圓形區域（以目標點為中心，以最近距離為半徑）
            # 與分割線相交時，才需要搜索另一側
            if abs(diff) < best[1]:
                search_recursive(far_child, depth + 1)
        
        search_recursive(self.root, 0)
        return best[0], best[1]
    
    def find_k_nearest(self, target: Point, k: int) -> List[Tuple[Point, float]]:
        """
        找到距離目標最近的 k 個點
        
        Args:
            target: 目標點
            k: 要找的點數
        
        Returns:
            以距離排序的 (點, 距離) 列表
        """
        if self.root is None:
            return []
        
        # 使用最大堆來追蹤最近的 k 個點
        candidates = []
        
        def search_recursive(node: KDNode, depth: int) -> None:
            if node is None:
                return
            
            distance = target.distance_to(node.point)
            
            # 添加到候選列表
            candidates.append((node.point, distance))
            candidates.sort(key=lambda x: x[1])
            
            # 只保留最近的 k 個
            if len(candidates) > k:
                candidates.pop()
            
            axis = depth % self.k
            diff = target.coordinates[axis] - node.point.coordinates[axis]
            
            near_child = node.left if diff < 0 else node.right
            far_child = node.right if diff < 0 else node.left
            
            search_recursive(near_child, depth + 1)
            
            # 如果候選列表少於 k 個，或者距離足夠近，則搜索另一側
            if len(candidates) < k or abs(diff) < candidates[-1][1]:
                search_recursive(far_child, depth + 1)
        
        search_recursive(self.root, 0)
        candidates.sort(key=lambda x: x[1])
        
        return candidates[:k]
    
    def range_search(self, center: Point, radius: float) -> List[Point]:
        """
        範圍搜索：找到以 center 為中心，radius 為半徑的球形區域內的所有點
        
        Args:
            center: 中心點
            radius: 半徑
        
        Returns:
            範圍內的點的列表
        """
        if self.root is None:
            return []
        
        results = []
        
        def search_recursive(node: KDNode, depth: int) -> None:
            if node is None:
                return
            
            distance = center.distance_to(node.point)
            
            # 如果在範圍內，添加到結果
            if distance <= radius:
                results.append(node.point)
            
            axis = depth % self.k
            diff = center.coordinates[axis] - node.point.coordinates[axis]
            
            # 搜索較近的一側
            near_child = node.left if diff < 0 else node.right
            far_child = node.right if diff < 0 else node.left
            
            search_recursive(near_child, depth + 1)
            
            # 如果分割線與圓相交，搜索另一側
            if abs(diff) <= radius:
                search_recursive(far_child, depth + 1)
        
        search_recursive(self.root, 0)
        return results
    
    def visualize(self, max_depth: int = 3) -> str:
        """
        可視化樹的結構（文字形式）
        
        Args:
            max_depth: 最多顯示的深度
        
        Returns:
            樹的字符串表示
        """
        if self.root is None:
            return "Empty tree"
        
        lines = []
        
        def traverse(node: KDNode, depth: int, prefix: str) -> None:
            if node is None or depth > max_depth:
                return
            
            # 計算分割軸
            axis = depth % self.k
            axis_names = ['X', 'Y', 'Z', 'W']
            axis_name = axis_names[axis] if axis < len(axis_names) else f"D{axis}"
            
            # 添加當前節點信息
            lines.append(
                f"{prefix}├─ {node.point.name} {node.point.coordinates} "
                f"[分割軸: {axis_name}]"
            )
            
            # 遞歸遍歷
            if node.left:
                traverse(node.left, depth + 1, prefix + "│  ")
            if node.right:
                traverse(node.right, depth + 1, prefix + "│  ")
        
        traverse(self.root, 0, "")
        return "\n".join(lines)
