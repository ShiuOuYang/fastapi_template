"""
KD-Tree 使用範例
================

這個文件展示了 KD-Tree 在各種實際場景中的應用
"""

from src.utils.kdtree import KDTree, Point


def example_1_basic_2d_search():
    """例子 1：二維空間的基本查詢"""
    print("\n" + "="*60)
    print("例子 1：二維空間的基本查詢")
    print("="*60)
    
    # 建立 6 個城市的坐標（簡化的 x, y 位置）
    cities = [
        Point([2, 3], "台北"),
        Point([5, 4], "台中"),
        Point([9, 6], "高雄"),
        Point([4, 7], "新竹"),
        Point([8, 1], "台南"),
        Point([7, 2], "嘉義"),
    ]
    
    # 構建 KD-Tree
    tree = KDTree(cities)
    
    # 顯示樹結構
    print("\n樹的結構:")
    print(tree.visualize())
    
    # 查詢最近的城市
    query = Point([6, 3], "查詢點")
    nearest, distance = tree.find_nearest(query)
    
    print(f"\n查詢點: {query}")
    print(f"最近的城市: {nearest}")
    print(f"距離: {distance:.2f}")
    
    # K-最近鄰搜索
    print(f"\n距離 {query} 最近的 3 個城市:")
    k_nearest = tree.find_k_nearest(query, k=3)
    for i, (point, dist) in enumerate(k_nearest, 1):
        print(f"  {i}. {point}: 距離 {dist:.2f}")


def example_2_range_search():
    """例子 2：範圍搜索 - 找到某個區域內的所有點"""
    print("\n" + "="*60)
    print("例子 2：範圍搜索 - 找到區域內的所有點")
    print("="*60)
    
    # 影院位置（x, y）
    cinemas = [
        Point([2, 3], "新竹影城"),
        Point([5, 4], "台中影城"),
        Point([9, 6], "高雄影城"),
        Point([4, 7], "竹北影城"),
        Point([8, 1], "台南影城"),
        Point([7, 2], "嘉義影城"),
        Point([1, 8], "宜蘭影城"),
        Point([9, 9], "屏東影城"),
    ]
    
    tree = KDTree(cinemas)
    
    # 用戶位置
    user_location = Point([5, 5], "用戶位置")
    search_radius = 4.0
    
    print(f"\n用戶位置: {user_location}")
    print(f"搜索半徑: {search_radius}")
    
    # 範圍搜索
    nearby_cinemas = tree.range_search(user_location, search_radius)
    
    print(f"\n範圍內的影院 ({len(nearby_cinemas)} 家):")
    for cinema in nearby_cinemas:
        dist = user_location.distance_to(cinema)
        print(f"  - {cinema}: 距離 {dist:.2f}")


def example_3_3d_space():
    """例子 3：三維空間搜索"""
    print("\n" + "="*60)
    print("例子 3：三維空間搜索 - 推薦系統")
    print("="*60)
    
    # 用戶特徵向量 (年齡, 消費金額, 活動天數)
    users = [
        Point([25, 1000, 10], "User A"),
        Point([26, 1100, 11], "User B"),
        Point([45, 5000, 20], "User C"),
        Point([24, 950, 9], "User D"),
        Point([30, 2000, 15], "User E"),
        Point([46, 5200, 21], "User F"),
        Point([27, 1200, 12], "User G"),
    ]
    
    tree = KDTree(users)
    
    # 目標用戶
    target_user = Point([25, 1000, 10], "Target User")
    
    print(f"\n目標用戶特徵: {target_user}")
    print("  [年齡, 消費金額, 活動天數]")
    
    # 找出最相似的用戶
    k = 3
    similar_users = tree.find_k_nearest(target_user, k=k)
    
    print(f"\n最相似的 {k} 個用戶:")
    for i, (user, distance) in enumerate(similar_users, 1):
        # 特徵距離越小，用戶越相似
        similarity = 1 / (1 + distance)
        print(f"  {i}. {user}: 相似度 {similarity:.2%}")


def example_4_dynamic_insertion():
    """例子 4：動態插入"""
    print("\n" + "="*60)
    print("例子 4：動態插入和查詢")
    print("="*60)
    
    # 建立空樹
    tree = KDTree()
    
    # 逐個插入點
    points_to_insert = [
        ("東京", [35.6762, 139.6503]),
        ("上海", [31.2304, 121.4737]),
        ("北京", [39.9042, 116.4074]),
        ("首爾", [37.5665, 126.9780]),
        ("台北", [25.0330, 121.5654]),
    ]
    
    print("\n插入點:")
    for name, coords in points_to_insert:
        point = Point(coords, name)
        tree.insert(point)
        print(f"  - 插入 {name}: {coords}")
    
    # 查詢
    query = Point([30.0, 120.0], "查詢點")
    print(f"\n查詢最近的 3 個城市（距離 {query}）:")
    
    nearest = tree.find_k_nearest(query, k=3)
    for i, (point, distance) in enumerate(nearest, 1):
        print(f"  {i}. {point.name}: 距離 {distance:.2f}°")


def example_5_feature_matching():
    """例子 5：圖片特徵匹配"""
    print("\n" + "="*60)
    print("例子 5：圖片特徵匹配")
    print("="*60)
    
    # 模擬圖片的特徵向量（實際應用中來自 CNN）
    # 特徵向量包含圖片的多個特徵值
    image_features = {
        "cat.jpg": [0.1, 0.2, 0.9, 0.1, 0.3, 0.8, 0.2, 0.1],
        "dog.jpg": [0.2, 0.3, 0.8, 0.2, 0.2, 0.7, 0.3, 0.2],
        "bird.jpg": [0.9, 0.1, 0.2, 0.9, 0.8, 0.1, 0.1, 0.9],
        "cat_2.jpg": [0.12, 0.22, 0.88, 0.12, 0.32, 0.79, 0.21, 0.11],
        "car.jpg": [0.3, 0.4, 0.5, 0.3, 0.4, 0.5, 0.3, 0.4],
    }
    
    # 建立特徵樹
    feature_points = [
        Point(features, name=img_name)
        for img_name, features in image_features.items()
    ]
    tree = KDTree(feature_points)
    
    # 查詢相似圖片
    query_features = image_features["cat.jpg"]
    query_point = Point(query_features, "cat.jpg")
    
    print(f"\n查詢圖片: cat.jpg")
    print(f"找出 3 張最相似的圖片:")
    
    similar_images = tree.find_k_nearest(query_point, k=3)
    
    for i, (point, distance) in enumerate(similar_images, 1):
        # 距離越小，相似度越高
        similarity = 1 / (1 + distance)
        print(f"  {i}. {point.name}: 特徵距離 {distance:.4f}, 相似度 {similarity:.2%}")


def example_6_performance_comparison():
    """例子 6：性能比較 - KD-Tree vs 暴力搜索"""
    print("\n" + "="*60)
    print("例子 6：性能比較")
    print("="*60)
    
    import time
    import random
    
    # 生成隨機點
    n = 1000
    random_points = [
        Point([random.uniform(0, 100), random.uniform(0, 100)])
        for _ in range(n)
    ]
    
    target = Point([50, 50], "Target")
    
    # KD-Tree 搜索
    tree = KDTree(random_points)
    
    start = time.time()
    nearest, distance = tree.find_nearest(target)
    kdtree_time = time.time() - start
    
    # 暴力搜索
    start = time.time()
    min_dist = float('inf')
    nearest_point = None
    for point in random_points:
        dist = target.distance_to(point)
        if dist < min_dist:
            min_dist = dist
            nearest_point = point
    brute_force_time = time.time() - start
    
    print(f"\n搜索 {n} 個隨機點中的最近鄰點")
    print(f"  KD-Tree 耗時: {kdtree_time*1000:.4f} ms")
    print(f"  暴力搜索耗時: {brute_force_time*1000:.4f} ms")
    print(f"  加速比: {brute_force_time/kdtree_time:.2f}x")


if __name__ == "__main__":
    print("\n" + "🌳 " * 20)
    print("KD-Tree 完整使用範例")
    print("🌳 " * 20)
    
    # 運行所有範例
    example_1_basic_2d_search()
    example_2_range_search()
    example_3_3d_space()
    example_4_dynamic_insertion()
    example_5_feature_matching()
    example_6_performance_comparison()
    
    print("\n" + "="*60)
    print("✅ 所有範例執行完成！")
    print("="*60 + "\n")
