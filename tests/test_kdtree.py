"""
KD-Tree 單元測試
===============

測試 KD-Tree 的各項功能
"""

import unittest
import math
from src.utils.kdtree import KDTree, Point


class TestPoint(unittest.TestCase):
    """測試 Point 類"""
    
    def test_point_creation(self):
        """測試點的建立"""
        p = Point([3, 4], "TestPoint")
        self.assertEqual(p.coordinates, [3, 4])
        self.assertEqual(p.name, "TestPoint")
        self.assertEqual(p.k, 2)
    
    def test_distance_calculation(self):
        """測試距離計算"""
        p1 = Point([0, 0], "P1")
        p2 = Point([3, 4], "P2")
        
        distance = p1.distance_to(p2)
        self.assertEqual(distance, 5.0)  # 3-4-5 三角形
    
    def test_3d_distance(self):
        """測試三維距離"""
        p1 = Point([0, 0, 0], "P1")
        p2 = Point([1, 2, 2], "P2")
        
        distance = p1.distance_to(p2)
        self.assertEqual(distance, 3.0)  # sqrt(1^2 + 2^2 + 2^2) = 3
    
    def test_dimension_mismatch(self):
        """測試維度不匹配"""
        p1 = Point([0, 0], "P1")
        p2 = Point([0, 0, 0], "P2")
        
        with self.assertRaises(ValueError):
            p1.distance_to(p2)


class TestKDTreeConstruction(unittest.TestCase):
    """測試 KD-Tree 的構建"""
    
    def setUp(self):
        """設置測試數據"""
        self.points = [
            Point([2, 3], "A"),
            Point([5, 4], "B"),
            Point([9, 6], "C"),
            Point([4, 7], "D"),
            Point([8, 1], "E"),
            Point([7, 2], "F"),
        ]
    
    def test_tree_construction(self):
        """測試樹的構建"""
        tree = KDTree(self.points)
        
        # 檢查根節點
        self.assertIsNotNone(tree.root)
        self.assertEqual(tree.k, 2)
        
        # 根節點應該是中位點
        self.assertIsNotNone(tree.root.point)
    
    def test_empty_tree_construction(self):
        """測試空樹"""
        tree = KDTree()
        self.assertIsNone(tree.root)
    
    def test_single_point(self):
        """測試單個點的樹"""
        points = [Point([5, 5], "Single")]
        tree = KDTree(points)
        
        self.assertIsNotNone(tree.root)
        self.assertEqual(tree.root.point.name, "Single")
        self.assertIsNone(tree.root.left)
        self.assertIsNone(tree.root.right)
    
    def test_tree_depth(self):
        """測試樹的深度"""
        tree = KDTree(self.points)
        
        def get_depth(node):
            if node is None:
                return 0
            return 1 + max(get_depth(node.left), get_depth(node.right))
        
        depth = get_depth(tree.root)
        # 6 個點應該有深度 3
        self.assertEqual(depth, 3)


class TestNearestNeighbor(unittest.TestCase):
    """測試最近鄰搜索"""
    
    def setUp(self):
        """設置測試數據"""
        self.points = [
            Point([2, 3], "A"),
            Point([5, 4], "B"),
            Point([9, 6], "C"),
            Point([4, 7], "D"),
            Point([8, 1], "E"),
            Point([7, 2], "F"),
        ]
        self.tree = KDTree(self.points)
    
    def test_nearest_neighbor_basic(self):
        """測試基本的最近鄰搜索"""
        target = Point([9, 2], "Target")
        nearest, distance = self.tree.find_nearest(target)
        
        # 最近的應該是 E (8, 1)
        self.assertEqual(nearest.name, "E")
        self.assertAlmostEqual(distance, math.sqrt(2), places=5)
    
    def test_nearest_neighbor_in_tree(self):
        """測試查詢點在樹中"""
        target = self.points[0]  # 查詢 A (2, 3)
        nearest, distance = self.tree.find_nearest(target)
        
        # 应该找到自己，距離為 0
        self.assertEqual(nearest.name, "A")
        self.assertEqual(distance, 0.0)
    
    def test_nearest_neighbor_empty_tree(self):
        """測試空樹的查詢"""
        tree = KDTree()
        target = Point([5, 5])
        
        nearest, distance = tree.find_nearest(target)
        self.assertIsNone(nearest)
        self.assertEqual(distance, float('inf'))


class TestKNearestNeighbor(unittest.TestCase):
    """測試 K-最近鄰搜索"""
    
    def setUp(self):
        """設置測試數據"""
        self.points = [
            Point([2, 3], "A"),
            Point([5, 4], "B"),
            Point([9, 6], "C"),
            Point([4, 7], "D"),
            Point([8, 1], "E"),
            Point([7, 2], "F"),
        ]
        self.tree = KDTree(self.points)
    
    def test_k_nearest_basic(self):
        """測試 K-最近鄰"""
        target = Point([5, 5], "Target")
        k_nearest = self.tree.find_k_nearest(target, k=3)
        
        self.assertEqual(len(k_nearest), 3)
        
        # 檢查距離遞增
        for i in range(len(k_nearest) - 1):
            self.assertLessEqual(k_nearest[i][1], k_nearest[i+1][1])
    
    def test_k_greater_than_n(self):
        """測試 K 大於點數"""
        target = Point([5, 5])
        k_nearest = self.tree.find_k_nearest(target, k=10)
        
        # 應該只返回 6 個（樹中所有的點）
        self.assertEqual(len(k_nearest), 6)
    
    def test_k_equals_1(self):
        """測試 K = 1"""
        target = Point([9, 2])
        nearest = self.tree.find_k_nearest(target, k=1)
        
        self.assertEqual(len(nearest), 1)
        # 應該是 E (8, 1)
        self.assertEqual(nearest[0][0].name, "E")


class TestRangeSearch(unittest.TestCase):
    """測試範圍搜索"""
    
    def setUp(self):
        """設置測試數據"""
        self.points = [
            Point([2, 3], "A"),
            Point([5, 4], "B"),
            Point([9, 6], "C"),
            Point([4, 7], "D"),
            Point([8, 1], "E"),
            Point([7, 2], "F"),
        ]
        self.tree = KDTree(self.points)
    
    def test_range_search_basic(self):
        """測試基本範圍搜索"""
        center = Point([7, 3], "Center")
        radius = 3.5
        results = self.tree.range_search(center, radius)
        
        # 驗證所有結果都在範圍內
        for point in results:
            distance = center.distance_to(point)
            self.assertLessEqual(distance, radius)
    
    def test_range_search_zero_radius(self):
        """測試零半徑範圍搜索"""
        target = self.points[0]
        results = self.tree.range_search(target, radius=0.1)
        
        # 應該只找到自己
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, "A")
    
    def test_range_search_large_radius(self):
        """測試大半徑範圍搜索"""
        center = Point([5, 5], "Center")
        radius = 100  # 很大的半徑
        results = self.tree.range_search(center, radius)
        
        # 應該找到所有點
        self.assertEqual(len(results), len(self.points))
    
    def test_range_search_no_points(self):
        """測試範圍內沒有點"""
        center = Point([100, 100], "Far")
        radius = 1
        results = self.tree.range_search(center, radius)
        
        self.assertEqual(len(results), 0)


class TestDynamicInsertion(unittest.TestCase):
    """測試動態插入"""
    
    def test_insert_into_empty_tree(self):
        """測試在空樹中插入"""
        tree = KDTree()
        point = Point([5, 5], "P1")
        tree.insert(point)
        
        self.assertIsNotNone(tree.root)
        self.assertEqual(tree.root.point.name, "P1")
    
    def test_insert_multiple_points(self):
        """測試插入多個點"""
        tree = KDTree()
        points = [
            Point([5, 5], "P1"),
            Point([3, 3], "P2"),
            Point([7, 7], "P3"),
        ]
        
        for point in points:
            tree.insert(point)
        
        # 查詢應該能找到所有插入的點
        target = Point([5, 5])
        nearest, distance = tree.find_nearest(target)
        self.assertEqual(distance, 0.0)
    
    def test_insert_dimension_mismatch(self):
        """測試插入不同維度的點"""
        points = [Point([5, 5], "P1")]
        tree = KDTree(points)
        
        # 嘗試插入不同維度的點
        with self.assertRaises(ValueError):
            tree.insert(Point([5, 5, 5], "P2"))


class TestHigherDimensions(unittest.TestCase):
    """測試高維空間"""
    
    def test_3d_space(self):
        """測試三維空間"""
        points = [
            Point([1, 2, 3], "P1"),
            Point([5, 6, 7], "P2"),
            Point([2, 3, 4], "P3"),
            Point([7, 8, 9], "P4"),
        ]
        
        tree = KDTree(points)
        
        target = Point([1.0, 2.0, 3.2])
        nearest, distance = tree.find_nearest(target)
        
        # 最近的應該是 P1 (距離 0.2)
        self.assertEqual(nearest.name, "P1")
    
    def test_5d_space(self):
        """測試五維空間"""
        points = [
            Point([1, 2, 3, 4, 5], "P1"),
            Point([2, 3, 4, 5, 6], "P2"),
            Point([0.5, 1.5, 2.5, 3.5, 4.5], "P3"),
        ]
        
        tree = KDTree(points)
        
        self.assertEqual(tree.k, 5)
        
        target = Point([1.1, 2.1, 3.1, 4.1, 5.1])
        nearest, distance = tree.find_nearest(target)
        
        self.assertEqual(nearest.name, "P1")


class TestVisualization(unittest.TestCase):
    """測試可視化"""
    
    def test_visualize_output(self):
        """測試可視化輸出"""
        points = [
            Point([2, 3], "A"),
            Point([5, 4], "B"),
            Point([9, 6], "C"),
        ]
        
        tree = KDTree(points)
        viz = tree.visualize()
        
        # 檢查輸出包含點的名稱
        self.assertIn("A", viz)
        self.assertIn("B", viz)
        self.assertIn("C", viz)
        # 檢查包含軸的信息
        self.assertIn("X", viz)
        self.assertIn("Y", viz)


if __name__ == "__main__":
    unittest.main()
