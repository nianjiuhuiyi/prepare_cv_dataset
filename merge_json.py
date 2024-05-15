"""
  合并两个同类标注json文件为一个json文件：(大家标注的类别都是一样的)
      before_json_path：好比这个是数据的前 100张：00000.jpg~00099.jpg
      after_json_path：好比这个是数据的后 100张：00100.jpg~00199.jpg
      result_path：这就把前面两个json文件合并成一个。
  """

import json
from datetime import datetime

before_json_path = r"./annotations1.json"
after_json_path = r"./annotations2.json"
result_path = r"./annotations.json"

if __name__ == '__main__':
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
