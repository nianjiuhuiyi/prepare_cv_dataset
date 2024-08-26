"""
    统计一个annotations.json文件里所有的类别，及其对应的每个类别的数量。
"""

import json
from collections import defaultdict


def count_coco_categories(annotations_file):
    # 创建一个默认字典来存储类别和它们的计数
    category_counts = defaultdict(int)

    with open(annotations_file, 'r', encoding="utf-8") as f:
        data = json.load(f)

    annotations = data.get("annotations")
    print("\n总的数量: ", len(annotations), "\n")

    # 类别名
    categories = [cate["name"] for cate in data.get("categories")]

    for annotation in data['annotations']:
        # 假设 'category_id' 是用于标识类别的字段
        # 在 COCO 数据集中，这通常是正确的
        category_id = annotation['category_id']
        # 更新该类别的计数
        category_counts[category_id] += 1

    print(category_counts)
    for category_id, count in sorted(category_counts.items()):
        print(f"Category Name: {categories[category_id]}, Count: {count}")


def count_categories(annotations_file):
    with open(annotations_file, 'r', encoding="utf-8") as f:
        data = json.load(f)

    annotations = data.get("annotations")
    print("\n总的数量: ", len(annotations), "\n")

    category_names = {cate["id"]: cate["name"] for cate in data.get("categories")}
    category_counts = {cate["name"]: 0 for cate in data.get("categories")}
    for annotation in annotations:
        category_id = annotation['category_id']
        category_counts[category_names.get(category_id)] += 1

    for i, (category, count) in enumerate(category_counts.items()):
        print(f"{i}, Category Name: {category}, Count: {count}")


if __name__ == '__main__':
    annotations_file = './annotations.json'
    # count_coco_categories(annotations_file)
    count_categories(annotations_file)
