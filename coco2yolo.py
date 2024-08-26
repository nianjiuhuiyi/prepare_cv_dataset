#!/usr/bin/env /root/anaconda3/bin/python
# linux下，可以像这样添加python的执行路径，然后给文件夹添加上执行权限，就能直接执行了

"""
    最终转换格式为YOLOV5中的参考：https://docs.ultralytics.com/yolov5/tutorials/train_custom_data/#11-create-datasetyaml
    理论上YOLO的格式都是这样差不多。
    COCO的数据目录可以有两种形式：
        形式一：coco.yaml
            path: ./datasets/coco  # dataset root dir
            train: train.txt  # train images (relative to 'path') 118287 images
            val: val.txt  # val images (relative to 'path') 5000 images
            # test: test-dev2017.txt
        # 它的数据是在./datasets/coco 中：
            .
            ├── images               # 所有的图都在这里
            │   ├── 00000.jpg
            │   ├── 00001.jpg
            │    ...........
            ├── labels               # 所有的标签都这这里
            │   ├── 00000.txt
            │   ├── 00001.txt
            │    ...........
            └── train.txt          # 通过.txt来做训练、验证的区分
            │
            └── val.txt

----------------------------------------------------------------------------------------------------
        形式二：coco.yaml    (这就没有labels这个文件夹了)
            path: ./datasets/coco     # dataset root dir
            train: images/train2017  # train images (relative to 'path') 128 images
            val: images/train2017  # val images (relative to 'path') 128 images
            test:  # test images (optional)
        # 它的数据是在 ./datasets/coco中，结构如下：
            .
            ├── images
            │   ├── test2017
            │   │     ├── 00000.jpg
            │   │     ├── 00001.jpg
            │   │     ...........
            │   ├── train2017
            │   └── val2017
            └── labels
                ├── test2017
                │     ├── 00000.txt
                │     ├── 00001.txt
                │     ...........
                ├── train2017
                └── val2017
            # 这就没有了 train.txt、val.txt了，这种就是要把图以及标签根据训练集、验证集分开

总结：
    1、这两种数据方式COCO官方都是支持的，下面的代码是做方式二的格式（包括得到bbox和segment）；
        这种一般是就一个整的json文件：annotation.json

    2、labelme得到的数据格式转coco的代码“my_labelme2yolo.py”，只做了bbox的生成；
        且它一般是 有 instant_train2017.json、instant_val2017.json 这种分来的
"""

import os
import json
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import numpy as np

np.random.seed(41)

# 这里的keys是放这里方便看的，没有用到。
keys = dict(
    套筒="T00",
    扭矩扳手="T01",
    套筒扳手="T02",
    开口扳手="T03",
    游标卡尺="T04",
    钢直尺="T05",
    水平尺="T06",
    斜度塞尺="T07",
    拉力计="T08",
    秒表="T09",
    绝缘电阻测试仪="T10"
)


class COCO2YOLO:
    def __init__(self, coco_json_path, save_path=r"./datasets/coco"):
        with open(coco_json_path, mode='r', encoding="utf-8") as fp:
            self.json_data = json.load(fp)

        self.save_path = save_path
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)

        self.categories = self._get_categories()
        self.images_info = self._get_images_info()
        self.annotations = self._process_annotations()

    def _get_categories(self):
        categories = {}
        for cls in self.json_data["categories"]:
            categories[cls["id"]] = cls["name"]
        return categories

    def _get_images_info(self):
        images_info = {}
        for image in self.json_data["images"]:
            image_id = image["id"]
            file_name = image["file_name"]
            if file_name.rfind("\\") != -1:
                file_name = file_name[file_name.rfind("\\") + 1:]
            w = image["width"]
            h = image["height"]
            images_info[image_id] = (file_name, w, h)
        return images_info

    def _min_index(self, arr1, arr2):
        """Find a pair of indexes with the shortest distance.
        Args:
            arr1: (N, 2).
            arr2: (M, 2).
        Return:
            a pair of indexes(tuple).
        """
        dis = ((arr1[:, None, :] - arr2[None, :, :]) ** 2).sum(-1)
        return np.unravel_index(np.argmin(dis, axis=None), dis.shape)

    def _merge_multi_segment(self, segments):
        """Merge multi segments to one list.
            Find the coordinates with min distance between each segment,
            then connect these coordinates with one thin line to merge all
            segments into one.

            Args:
                segments(List(List)): original segmentations in coco's json file.
                    like [segmentation1, segmentation2,...],
                    each segmentation is a list of coordinates.
            """
        s = []
        segments = [np.array(i).reshape(-1, 2) for i in segments]
        idx_list = [[] for _ in range(len(segments))]

        # record the indexes with min distance between each segment
        for i in range(1, len(segments)):
            idx1, idx2 = self._min_index(segments[i - 1], segments[i])
            idx_list[i - 1].append(idx1)
            idx_list[i].append(idx2)

        # use two round to connect all the segments
        for k in range(2):
            # forward connection
            if k == 0:
                for i, idx in enumerate(idx_list):
                    # middle segments have two indexes
                    # reverse the index of middle segments
                    if len(idx) == 2 and idx[0] > idx[1]:
                        idx = idx[::-1]
                        segments[i] = segments[i][::-1, :]

                    segments[i] = np.roll(segments[i], -idx[0], axis=0)
                    segments[i] = np.concatenate([segments[i], segments[i][:1]])
                    # deal with the first segment and the last one
                    if i in [0, len(idx_list) - 1]:
                        s.append(segments[i])
                    else:
                        idx = [0, idx[1] - idx[0]]
                        s.append(segments[i][idx[0]:idx[1] + 1])

            else:
                for i in range(len(idx_list) - 1, -1, -1):
                    if i not in [0, len(idx_list) - 1]:
                        idx = idx_list[i]
                        nidx = abs(idx[1] - idx[0])
                        s.append(segments[i][nidx:])
        return s

    def _process_annotations(self):
        """
        一张图的目标放一起,Key是image_id，
            value是一个list，对应的是这张图上所有目标，[(0, [12, 13, 55, 66, 77, 88, ...]), ...]
        :return:
        """
        annotations = {}
        for annotation in self.json_data["annotations"]:
            image_id = annotation["image_id"]
            category_id = annotation["category_id"]
            bbox = annotation["bbox"]
            # TODO:注意后面若是有些没有分割标注，这里要做一个容错判断
            segmentation = annotation["segmentation"]
            # 会有分割区域是多个部分的，即 segmentation 是 [[]] ，大多数情况 len(segmentation) = 1,所以以前常直接segmentation[0]
            # 现在不为区域个数不为1时就要合并，方法是来自yolov5的官方：https://github.com/ultralytics/JSON2YOLO/blob/c38a43f342428849c75c103c6d060012a83b5392/general_json2yolo.py#L295
            if len(segmentation) > 1:
                # 合并的方法
                segmentation = self._merge_multi_segment(segmentation)
                segmentation = np.concatenate(segmentation, axis=0).reshape(-1).tolist()
            else:
                segmentation = segmentation[0]

            annotations.setdefault(image_id, [])
            annotations.get(image_id).append((category_id, bbox, segmentation))
        return annotations

    def _coco2yolo(self, part_name_list: list, type_name: str, use_segment: bool):
        """
        if no objects in image, no *.txt file is required
        :param part_name_list: 对应train或val、test图片的image_id组成的列表
        :param type_name: 传入'train', 或者 'valid'这样的字符串,以生成train.txt或者valid.txt
        :return:
        """
        labels_path = os.path.join(self.save_path, "labels")   # like this "datasets/coco/labels/"
        if not os.path.exists(labels_path):
            os.makedirs(labels_path)

        # 总的例如“train.txt”是用来存放所有训练集的图片路径，一行记录一张图片的路径
        total_label = open(f"{self.save_path}/{type_name}.txt", mode='w', encoding="utf-8")

        for val_file in tqdm(part_name_list, desc=f"{type_name}: "):
            file_name, img_w, img_h = self.images_info.get(val_file)
            total_label.write("{}/images/{}\n".format(self.save_path, file_name))
            total_label.flush()

            # if no objects in image, no *.txt file is required
            # 看到yolo官方的处理中，会把没有目标的图给删除，我在想是不是也删掉(不删，在yolov5中就默认是背景图)
            annotations = self.annotations.get(val_file)
            if not annotations:
                continue

            save_label_path = os.path.join(labels_path, file_name.split('.')[0] + ".txt")
            label_txt = open(save_label_path, mode='w', encoding="utf-8")

            if use_segment:
                for annotation in annotations:
                    category_id, _, segmentation = annotation
                    # 坐标归一化
                    segmentation = (np.array(segmentation).reshape(-1, 2) / np.array([img_w, img_h])).reshape(
                        -1).tolist()
                    label_txt.write("{} {}\n".format(category_id, ' '.join(map(str, segmentation))))
                    label_txt.flush()
            else:
                for annotation in annotations:
                    category_id, bbox, _ = annotation
                    x, y, w, h = bbox
                    center_x = x + w / 2
                    center_y = y + h / 2

                    label_txt.write("{} {} {} {} {}\n".format(
                        category_id, center_x / img_w, center_y / img_h, w / img_w, h / img_h
                    ))  # box中心点坐标、box的宽高
                    label_txt.flush()
            label_txt.close()
        total_label.close()

    def run(self, train_size, use_segment=False):
        """
        默认仅生成训练集和验证集，不做测试集。
        :param train_size: 训练集所占比重（0-1）
        :param use_segment: 默认为False,即生成的数据是box的框检测，为True就是生成的数据是分割的
        :return:
        """
        # 得到的是对应类别的images_info的key，它就是annotations中的"image_id"，也是images中的“id”
        train_files, val_files = train_test_split(list(self.images_info.keys()), train_size=train_size)
        self._coco2yolo(train_files, "train", use_segment=use_segment)
        self._coco2yolo(val_files, "val", use_segment=use_segment)


if __name__ == '__main__':

    # 同时生成 det、seg 的标签。
    flag = False
    for save_path in ["datasets/coco/det", "datasets/coco/seg"]:
        if save_path.endswith("seg"):
            flag = True    

        # 下面保存路径结尾千万能带/符号，即绝不能是datasets/coco/
        # 也绝对不能是 ./datasets/coco 这样写，这样写后，yolov5训练时拼接出来的地址不对，会找不到图片路径
        obj = COCO2YOLO(r"./annotations.json", save_path=save_path)
        # 修改 use_segment 的值来生成目标检测还是分割的标签
        obj.run(train_size=0.9, use_segment=flag)

