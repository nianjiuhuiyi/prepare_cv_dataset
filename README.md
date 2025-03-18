# prepare_cv_dataset
用于准备各类检测数据之间的转换。

其它类型的转换参考项目：[prepare_detection_dataset](https://github.com/spytensor/prepare_detection_dataset)、[Label2Everything](https://github.com/TommyZihao/Label2Everything)、[LabelConvert](https://github.com/RapidAI/LabelConvert)(v5-v8之间的转换)。

1. [coco2yolo.py](./coco2yolo.py)：coco数据格式转成yolo的数据格式
   - 注意去看代码里最后一行，是决定转成分割的数据还是检测的数据。默认是转成分割的格式。
   - [cocoviewer.py](./cocoviewer.py)：coco数据格式查看。用法`python cocoviewer.py -i ./datasets -a ./datasets/annotations.json`。要注意annotation.json中图片路径是什么样的。这个代码来自于[SAM-Tool](https://github.com/nianjiuhuiyi/SAM-Tool)。
   - [verify_yolo_labels.py](./verify_yolo_labels.py)：yolo数据格式查看。
2. [merge_json.py](./merge_json.py)：把两个同标注类别，图片是前后顺序的json标注文件融合到一起。
   - [transfer.py](./transfer.py)：这是将标注文件的标签从中文转换到英文。
   - [counts.py](./counts.py)：统计一个annotations.json文件里所有的类别，及其对应的每个类别的数量
3. [labelme2yolov8Pose.py](./labelme2yolov8Pose.py)：将labelme标注的关键点格式转成yolov8关键点的数据格式。
4. [grab_image.py](./grab_image.py)：多/单路相机同时进行采图。
   - [video2frame.py](./video2frame.py)：将视频抽帧成图片。
5. [contour_matting.py](./contour_matting.py)：把目标沿其轮廓或是最小外接矩形从原图中抠出来，并贴到一个纯黑或纯白的背景中。

---

另外不新建文件了：

- 获取annotations.json的所有类别名称，用英文,号隔开

  ```python
  import json
  
  with open("annotations.json", 'r', encoding="utf-8") as fp:
      data = json.load(fp)
  
  categories = []
  for category in data.get("categories"):
      categories.append(category.get("name"))
  
  print(','.join(categories))
  ```

- 针对win批量改名后图片再次进行批量重命名：（先按照前面字母排序，字母一样的时候就会按照括号里的数字大小排序）

  ```python
  import glob
  import os
  
  # 传进来的win批量命名的图片名称，如 "a (1).jpg"
  def my_sort(x: str):
      x = x.split(' ')  #  ['a', '(1).jpg'] 
      first = x[0]
      second = x[1].split('.')[0]     # (1)  (10)  (11)  之类的结果
      second = second.strip('(').strip(')')   # 1  10  11  之类的string
      return (first, int(second))   # 记得要把是string类型的数字转成int
  
  begin_num = 123
  
  imgs_name = glob.glob("*.jpg")
  imgs_name.sort(key=my_sort)
  print(imgs_name)
  for img_name in imgs_name:
      os.rename(img_name, f"{begin_num:05d}.jpg")
      begin_num += 1
  print("Done!")
  ```

  说明：
  
  - 单纯的imgs_name.sort()，就会得到类似这样的结果：
    ['a (1).jpg', 'a (10).jpg', 'a (11).jpg', , 'a (2).jpg', 'a (20).jpg', 'a (21).jpg',  'a (3).jpg', 'a (4).jpg', 'a (5).jpg', 'a (6).jpg', 'a (7).jpg', 'a (8).jpg', 'a (9).jpg', 'b (1).jpg', 'b (10).jpg', 'b (11).jpg', 'b (2).jpg', 'b (3).jpg']
  - imgs_name.sort(key=len)，就会得到类似这样的效果：
    ['a (1).jpg', 'a (2).jpg', 'a (9).jpg', 'b (1).jpg', 'b (2).jpg', 'b (9).jpg', 'c (1).jpg', 'c (2).jpg', 'c (9).jpg', 'a (10).jpg', 'a (11).jpg', 'b (10).jpg', 'b (11).jpg', 'b (12).jpg', 'c (10).jpg', 'c (11).jpg', 'c (12).jpg']
  - 通过上面按两个字段自定义排序后，就会得到想要的效果：（即先按前面字母排序，字母相同时再按后面括号里数字排序）
    ['a (1).jpg', 'a (2).jpg', 'a (9).jpg', 'a (10).jpg', 'a (11).jpg', 'b (1).jpg', 'b (2).jpg', 'b (9).jpg', 'b (10).jpg', 'b (11).jpg', 'b (12).jpg', 'c (1).jpg', 'c (2).jpg', 'c (9).jpg', 'c (10).jpg', 'c (11).jpg', 'c (12).jpg']

