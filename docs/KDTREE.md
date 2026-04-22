# KD-Tree（K 維樹）教學指南

## 📚 目錄
1. [什麼是 KD-Tree](#什麼是-kd-tree)
2. [核心概念](#核心概念)
3. [使用範例](#使用範例)
4. [實際應用](#實際應用)
5. [性能分析](#性能分析)

---

## 什麼是 KD-Tree

**KD-Tree（K-Dimensional Tree）** 是一種多維空間分割資料結構，用於組織和搜索 K 維空間中的點。

### 🎯 主要應用
- **最近鄰搜索**：快速找到距離某點最近的點
- **範圍搜索**：找到某個區域內的所有點
- **圖像處理**：特徵匹配、色彩搜索
- **推薦系統**：用戶相似度計算
- **GPS 應用**：查找附近的地點

---

## 核心概念

### 1️⃣ 分割軸原理

在每一層按照不同的維度進行分割：

```
二維空間 (x, y)：
第 0 層：按 X 軸分割
第 1 層：按 Y 軸分割
第 2 層：按 X 軸分割（循環）
...

三維空間 (x, y, z)：
第 0 層：按 X 軸分割
第 1 層：按 Y 軸分割
第 2 層：按 Z 軸分割
第 3 層：按 X 軸分割（循環）
...
```

### 2️⃣ 構建流程

```
輸入: [(2,3), (5,4), (9,6), (4,7), (8,1), (7,2)]

1. 深度 0，按 X 軸分割
   中位點：(7,2)
         ┌─────┴─────┐
        左         右
   
2. 左子樹，按 Y 軸分割
   左子樹點：[(2,3), (5,4), (4,7)]
   中位點：(4,7)
   
3. 右子樹，按 Y 軸分割
   右子樹點：[(9,6), (8,1)]
   中位點：(8,1)

最終樹結構：
           (7,2)
          /     \
       (4,7)   (8,1)
       /   \     /
    (2,3) (5,4) (9,6)
```

### 3️⃣ 搜索策略

**最近鄰搜索流程：**

1. 從根開始，像二進制搜索樹那樣遍歷
2. 記錄目前找到的最近點
3. **關鍵優化**：只有當分割線與搜索范圍相交時，才搜索另一側

```python
# 判斷是否需要搜索另一側：
if abs(目標座標 - 當前座標) <= 最近距離:
    搜索另一側
```

---

## 使用範例

### 基本使用

```python
from src.utils.kdtree import KDTree, Point

# 1. 建立二維點
points = [
    Point([2, 3], "A"),
    Point([5, 4], "B"),
    Point([9, 6], "C"),
    Point([4, 7], "D"),
    Point([8, 1], "E"),
    Point([7, 2], "F"),
]

# 2. 構建 KD-Tree
tree = KDTree(points)

# 3. 可視化樹結構
print(tree.visualize())
```

**輸出：**
```
├─ F (7, 2) [分割軸: X]
│  ├─ D (4, 7) [分割軸: Y]
│  │  ├─ A (2, 3) [分割軸: X]
│  │  └─ B (5, 4) [分割軸: X]
│  └─ E (8, 1) [分割軸: Y]
│     └─ C (9, 6) [分割軸: Y]
```

### 最近鄰搜索

```python
# 查詢距離 (9, 2) 最近的點
target = Point([9, 2], "TARGET")
nearest_point, distance = tree.find_nearest(target)

print(f"最近的點: {nearest_point}")
print(f"距離: {distance:.2f}")

# 輸出示例:
# 最近的點: E(8, 1)
# 距離: 1.41
```

### K-最近鄰搜索

```python
# 查詢距離 (9, 2) 最近的 3 個點
k_nearest = tree.find_k_nearest(target, k=3)

for point, distance in k_nearest:
    print(f"{point}: 距離 {distance:.2f}")

# 輸出示例:
# E(8, 1): 距離 1.41
# F(7, 2): 距離 2.00
# C(9, 6): 距離 4.00
```

### 範圍搜索

```python
# 查詢在 (7, 3) 周圍 3.5 單位範圍內的所有點
center = Point([7, 3], "CENTER")
radius = 3.5
points_in_range = tree.range_search(center, radius)

print(f"範圍內的點:")
for point in points_in_range:
    dist = center.distance_to(point)
    print(f"  {point}: 距離 {dist:.2f}")

# 輸出示例:
# 範圍內的點:
#   E(8, 1): 距離 2.24
#   F(7, 2): 距離 1.00
#   D(4, 7): 距離 4.47
```

### 動態插入

```python
# 創建一個空樹，然後動態插入點
tree = KDTree()
tree.insert(Point([2, 3], "A"))
tree.insert(Point([5, 4], "B"))
tree.insert(Point([9, 6], "C"))

# 插入新點
tree.insert(Point([1, 1], "NEW"))

print(tree.visualize())
```

---

## 實際應用

### 🖼️ 應用 1：圖像特徵匹配

```python
# 場景：在圖像庫中找到最相似的圖片

feature_vectors = {
    "image1.jpg": [0.2, 0.8, 0.1, 0.9],
    "image2.jpg": [0.3, 0.7, 0.2, 0.8],
    "image3.jpg": [0.9, 0.1, 0.8, 0.2],
    "image4.jpg": [0.21, 0.79, 0.12, 0.91],
}

# 構建 KD-Tree
points = [
    Point(features, name=img_name)
    for img_name, features in feature_vectors.items()
]
tree = KDTree(points)

# 查詢相似圖片
query_feature = Point([0.2, 0.8, 0.1, 0.9])
similar_images = tree.find_k_nearest(query_feature, k=2)

for point, distance in similar_images:
    print(f"相似圖片: {point.name}, 特徵距離: {distance:.4f}")
```

### 🗺️ 應用 2：GPS 位置搜索

```python
# 場景：找到用戶周圍 5km 內的所有餐廳

restaurants = {
    "餐廳A": [25.0330, 121.5654],  # [緯度, 經度]
    "餐廳B": [25.0328, 121.5652],
    "餐廳C": [25.0450, 121.5700],
    "餐廳D": [25.0320, 121.5700],
}

points = [
    Point(coords, name=name)
    for name, coords in restaurants.items()
]
tree = KDTree(points)

# 查詢用戶位置周圍的餐廳（簡化：使用歐幾里得距離）
user_location = Point([25.0330, 121.5655])
nearby_restaurants = tree.range_search(user_location, radius=0.01)  # 約 1km

for restaurant in nearby_restaurants:
    dist = user_location.distance_to(restaurant)
    print(f"{restaurant.name}: 距離 {dist:.6f}°")
```

### 👥 應用 3：推薦系統

```python
# 場景：推薦相似的用戶

user_profiles = {
    "user1": [25, 8.5, 1],      # [年齡, 評分, 活動頻率]
    "user2": [26, 8.3, 1.1],
    "user3": [45, 7.0, 0.5],
    "user4": [24, 8.4, 1.05],
}

points = [
    Point(profile, name=name)
    for name, profile in user_profiles.items()
]
tree = KDTree(points)

# 為 user1 推薦相似用戶
user1_profile = Point([25, 8.5, 1])
similar_users = tree.find_k_nearest(user1_profile, k=2)

for point, distance in similar_users:
    print(f"推薦: {point.name}, 相似度: {1 / (1 + distance):.2%}")
```

---

## 性能分析

### ⏱️ 時間複雜度

| 操作 | 平均複雜度 | 最壞複雜度 | 說明 |
|------|----------|---------|------|
| 構建 | O(n log n) | O(n log n) | 需要排序 |
| 查詢 | O(log n) | O(n) | 最壞為退化成一維搜索 |
| K-最近鄰 | O(k log n) | O(n) | 取決於點的分佈 |
| 範圍搜索 | O(√n + m) | O(n) | m 為結果數量 |
| 插入 | O(log n) | O(n) | 取決於樹的平衡情況 |

### 💾 空間複雜度

- **O(n)**：存儲 n 個點需要 O(n) 的空間

### 📊 什麼時候性能最好？

✅ **最好的情況：**
- 點均勻分佈在空間中
- 進行最近鄰搜索而非範圍搜索
- K 值遠小於 n（K-最近鄰搜索）

❌ **不適合的情況：**
- 維度很高（10+ 維）：「維度詛咒」問題
- 頻繁的動態插入和刪除
- 點高度聚集在某個區域

---

## 優化建議

### 1. 平衡樹

保持樹的平衡能提高查詢性能：

```python
def is_balanced(node):
    """檢查樹是否平衡"""
    if node is None:
        return True
    
    if node.left is None and node.right is None:
        return True
    
    if node.left is None:
        left_height = 0
    else:
        left_height = get_height(node.left)
    
    if node.right is None:
        right_height = 0
    else:
        right_height = get_height(node.right)
    
    return (abs(left_height - right_height) <= 1 and
            is_balanced(node.left) and
            is_balanced(node.right))
```

### 2. 使用球面距離（地理應用）

```python
import math

def haversine_distance(lon1, lat1, lon2, lat2):
    """計算兩個經緯度點的真實距離（km）"""
    R = 6371  # 地球半徑（km）
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    
    c = 2 * math.asin(math.sqrt(a))
    return R * c
```

### 3. 高維數據的替代方案

對於高維數據，考慮：
- **LSH（Locality Sensitive Hashing）**
- **Ball Tree**：比 KD-Tree 在高維更有效
- **Product Quantization**：用於大規模數據

---

## 總結

| 特性 | 評分 |
|------|------|
| 易於理解 | ⭐⭐⭐⭐⭐ |
| 實現難度 | ⭐⭐⭐☆☆ |
| 查詢速度 | ⭐⭐⭐⭐☆ |
| 維度適應性 | ⭐⭐⭐☆☆ |
| 動態性能 | ⭐⭐⭐☆☆ |

KD-Tree 是一個強大且優雅的資料結構，特別適合在低到中等維度的空間中進行最近鄰搜索。
