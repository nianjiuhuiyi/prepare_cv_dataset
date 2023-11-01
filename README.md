# prepare_cv_dataset
用于准备各类检测数据之间的转换。

其它类型的转换参考项目：[prepare_detection_dataset](https://github.com/spytensor/prepare_detection_dataset)

- coco2yolo.py：注意去看代码里最后一行，是决定转成分割的数据还是检测的数据。默认是转成分割的格式。
- cocoviewer.py：用法`python cocoviewer.py -i ./datasets -a ./datasets/annotations.json`  # 要注意annotation.json中图片路径是什么样的。这个代码来自于SAM-Tool
