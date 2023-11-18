import time
import os
import shutil
import json
import glob
from typing import Any

from sklearn.model_selection import train_test_split
from tqdm import tqdm

import numpy as np
np.random.seed(41)       # 为train_test_split设一个随机种子，保证每次运行都结果一致

keys = dict(
    扭矩扳手=0,
    游标卡尺=1,
    斜度塞尺=2
)


class LABELME2YOLO:
    def __init__(self, source_path: str, save_dir="datasets/coco/", if_test=False):
        """
        :param source_path: labelme标注结果的目录的路径，里面应包含了图片和其对应的json标注文件
        :param save_dir: 这是针对yolov5的，默认就是这么放的，这个路径会影响生成的.txt标注文件
        :param if_test: 是否启用测试集，一般数据少，不启用
        :return:
        """
        self.labelme_path = source_path
        self.if_test = if_test

        self.save_dir = save_dir
        self.imgs_dir = os.path.join(self.save_dir, "images")  # 总的图放的路径
        self.labels_dir = os.path.join(self.save_dir, "labels")  # 总的txt的label放的路径
        for path in [self.save_dir, self.imgs_dir, self.labels_dir]:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
        
    def _load_json(self, part_json_list: list, name: str):
        """

        :param part_json_list: 一个元素均为json文件名称的列表
        :param name: 传入'train', 或者 'val'这样的字符串,以生成train.txt或者val.txt
        :return:
        """
        train_label = open(os.path.join(self.save_dir, f'{name}.txt'), 'w', encoding="utf-8")   # datasets/coco/train.txt
        for train_file in tqdm(part_json_list, f"{name}"):
            with open(os.path.join(self.labelme_path, train_file), encoding='utf-8') as f:
                data = json.load(f)
            image_w = data['imageWidth']
            image_h = data['imageHeight']
            # datasets/coco/images/00293.jpg  # 这是yolov5
            # data/custom/images/00293.jpg   # 之前yolov3可能就是这种的
            train_label.write("{}/{}.jpg\n".format(self.imgs_dir, train_file.split('.')[0]))

            classes_list = data['shapes']  # a list（一个元素是一个物品）
            label_txt = open(os.path.join(self.labels_dir, train_file.split('.')[0] + '.txt'), 'w', encoding="utf-8")
            for classes in classes_list:
                label = classes['label']
                points = np.array(classes['points'])
                x1, y1 = min(points[:, 0]), min(points[:, 1])
                x2, y2 = max(points[:, 0]), max(points[:, 1])
                center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
                w, h = x2 - x1, y2 - y1
                label_txt.write('{} {} {} {} {}\n'.format(
                    keys[label], center_x / image_w, center_y / image_h, w / image_w, h / image_h
                ))  # （标签，归一化后的框的中心点坐标及其w,h）
            label_txt.close()
            train_label.flush()
        train_label.close()

    def __call__(self, test_size=0.1):
        """

        :param test_size: 验证集所占总数据集的比例
        :return:
        """
        all_files = os.listdir(self.labelme_path)
        label_files = [file for file in all_files if file.split('.')[-1] == 'json']  # 一个元素是一个json文件的名字
        image_files = glob.glob(self.labelme_path + "/*.jpg")  # 列表，包含所有的图片，一个元素是一张图片的绝对地址

        if self.if_test:  # 如果要生成测试集
            test_size += 0.05
            train_files, test_val_files = train_test_split(label_files, test_size=test_size)
            test_files, val_files = train_test_split(test_val_files, test_size=test_size)
            print("train_n:", len(train_files), 'test_n:', len(test_files), 'val_n:', len(val_files))
            self._load_json(part_json_list=test_files, name="test")
        else:
            train_files, val_files = train_test_split(label_files, test_size=test_size)

        self._load_json(part_json_list=train_files, name="train")
        self._load_json(part_json_list=val_files, name="val")
        print("标签已经处理完毕！")

        # 将图片复制到对应的路径./images目录下；然后通过train.txt、val.txt、test.txt去取
        for image_file_path in tqdm(image_files, "图像复制中"):
            shutil.copy(image_file_path, self.imgs_dir)
        print("Everything is OK!")
        

if __name__ == '__main__':
    # 主要是针对yolov5的，其它可能有一点出入，具体就要看情况去进行修改了
    start_time = time.time()
    file_path = r"./all"         # 路径下应该是所有的图片和labelme标注的json文件
    LABELME2YOLO(source_path=file_path)()
    end_time = time.time()
    print("总用时:{:.2f}分钟".format((end_time - start_time) / 60))
