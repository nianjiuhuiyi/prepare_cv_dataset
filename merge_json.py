
"""
    此程序默认是将 dir_path 路径中的的所有文件夹(如01、02、03、...)中的annotations合并成一个annotations.json
    也可单独把merge函数拿出来，用来合并两个annotations.json为一个annotations.json
"""

import os
import json
from datetime import datetime


def merge(before_json_path: str, after_json_path: str, result_path = r"./annotations.json"):
    """
    合并两个同类标注json文件为一个json文件：(大家标注的类别都是一样的)
    :param before_json_path: 第一个json注释文件annotations1.json，里面好比是这个数据的前100张：00000.jpg~00099.jpg
    :param after_json_path: 第二个json注释文件annotations2.json，里面好比这个是数据的后100张：00100.jpg~00199.jpg
    :param result_path: 最终两个json文件合成的结果文件, defaults to r"./annotations.json"
    """
    # before_json_path = r"./annotations1.json"
    # after_json_path = r"./annotations2.json"
    # result_path = r"./annotations.json"
    
    with open(before_json_path, mode='r', encoding="utf-8") as fp:
        before_data = json.load(fp)
    with open(after_json_path, mode='r', encoding="utf-8") as fp:
        after_data = json.load(fp)

    print(before_data.get("categories"))
    print()
    print(after_data.get("categories"))

    # 确保类别是相同的（如果不同，自己把控类别数，然后把这去掉）
    assert before_data.get("categories") == after_data.get("categories"), "两个json文件的类别不一致..."

    images = before_data.get("images")  # 前者json的图片列表
    annotations = before_data.get("annotations")  # 前者的所有标注的列表

    # 获取到他们的长度，也就是后者json开始的数字
    befotr_img_nums = len(images)
    brfore_anno_muns = len(annotations)

    # 改后者图片的id
    for item in after_data.get("images"):
        item["id"] += befotr_img_nums

    # 改后者的注释文件的id(目标个数)、image_id(对应的图片id也增加了)
    for item in after_data.get("annotations"):
        item["id"] += brfore_anno_muns
        item["image_id"] += befotr_img_nums

    # 合并成一个json
    result = dict(
        info=before_data.get("info"),
        images=before_data.get("images") + after_data.get("images"),
        annotations=before_data.get("annotations") + after_data.get("annotations"),
        # 如果后面的json在最后面新增了类别，那最终类别可以以后面的json类别为准，即：categories=after_data.get("categories")
        # categories=before_data.get("categories")
        categories=after_data.get("categories")
    )

    # 更新一下时间
    result["info"]["date_created"] = datetime.now().strftime("%Y/%m/%d")

    with open(result_path, mode='w', encoding="utf-8") as fp:
        json.dump(result, fp, ensure_ascii=False)

    print("Done!")


if __name__ == '__main__':

    dir_path = r"I:\SAM-workTable-0815\dataset"
    files = os.listdir(dir_path)
    print(files)
    # files = sorted(files, key=lambda x: int(x))
    files.sort(key=lambda x: int(x))
    print(files)

    all_json_path = []
    for file in files:
        json_path = os.path.join(dir_path, file, "annotations.json")
        all_json_path.append(json_path)
    
    print(all_json_path)

    # 先把前两个合并放起来：
    result = "./annotations.json"
    merge(all_json_path[0], all_json_path[1], result)
    # 再把剩下的合并
    for i in range(2, len(all_json_path)):
        merge(result, all_json_path[i], result)

    print("Done!")
    