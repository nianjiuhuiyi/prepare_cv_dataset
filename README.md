# prepare_cv_dataset
用于准备各类检测数据之间的转换。

其它类型的转换参考项目：[prepare_detection_dataset](https://github.com/spytensor/prepare_detection_dataset)、[Label2Everything](https://github.com/TommyZihao/Label2Everything)。

1. [coco2yolo.py](./coco2yolo.py)：coco数据格式转成yolo的数据格式
   - 注意去看代码里最后一行，是决定转成分割的数据还是检测的数据。默认是转成分割的格式。
   - [cocoviewer.py](./cocoviewer.py)：coco数据格式查看。用法`python cocoviewer.py -i ./datasets -a ./datasets/annotations.json`。要注意annotation.json中图片路径是什么样的。这个代码来自于[SAM-Tool](https://github.com/nianjiuhuiyi/SAM-Tool)。
   - [verify_yolo_labels.py](./verify_yolo_labels.py)：yolo数据格式查看。
2. [merge_json.py](./merge_json.py)：把两个同标注类别，图片是前后顺序的json标注文件融合到一起。
   - [transfer.py](./transfer.py)：这是将标注文件的标签从中文转换到英文。
   - [counts.py](./counts.py)：统计一个annotations.json文件里所有的类别，及其对应的每个类别的数量
3. [labelme2yolov8Pose.py](./labelme2yolov8Pose.py)：将labelme标注的关键点格式转成yolov8关键点的数据格式。
4. [grab_image.py](./grab_image.py)：多/单路相机同时进行采图。
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

  

