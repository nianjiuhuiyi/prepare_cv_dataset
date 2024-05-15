"""
这个脚本使用的背景是：
    1、使用labelme进行游标卡尺标注，一张图上只有一个游标卡尺，也只有这个类别;
    2、先是用矩形框标注了游标卡尺，类名为“ruler”，
    3、再用关键点标注了游标卡尺的三个关键点，类名为“A”、“B”、“C”;

目的：
    将labelme标注的数据格式转换为yolov8的数据格式。
-------------------------------------------------------------------------------

给到的labelme的数据路径：./dataset/YBKC
    YBKC
    ├── 00000.jpg
    ├── 00000.json
    ├── 00001.jpg
    ├── 00001.json
    ├── 00002.jpg
    ├── 00002.json
     ...........

执行完后，会在此脚本路径生成对应的yolov8的数据格式：
    .
    ├── images
    │   ├── 00000.jpg
    │   ├── 00001.jpg
    │   ├── 00002.jpg
    │    ...........
    └── labels
    │   ├── 00000.txt
    │   ├── 00001.txt
    │   ├── 00002.txt
    │    ...........
    ├── train.txt
    └── val.txt
"""

import time
import os
import shutil
import json
import numpy as np
from sklearn.model_selection import train_test_split
import glob
from tqdm import tqdm
np.random.seed(41)       # 为train_test_split设一个随机种子，保证每次运行都结果一致


def load_json(part_json_list, name):
    """

    :param part_json_list: 一个元素均为json文件名称的列表
    :param name: 传入'train', 或者 'valid'这样的字符串,以生成train.txt或者valid.txt
    :return:
    """

    train_label = open(f'{name}.txt', 'w')
    for train_file in tqdm(part_json_list, f"{name}"):
        with open(os.path.join(json_path, train_file), encoding='utf-8') as f:
            data = json.load(f)
        image_w = data['imageWidth']
        image_h = data['imageHeight']
        train_label.write("dataset/images/{}.jpg\n".format(train_file.split('.')[0]))

        classes_list = data['shapes']  # a list（一个元素是一个物品）
        label_txt = open(os.path.join('./labels', train_file.split('.')[0] + '.txt'), 'w')

        temp_result = dict()   # 把列表转成字典，更方便后续按顺序取出
        for classes in classes_list:
            temp_result[classes['label']] = classes['points']

        result = [0]         # 0 代表默认的类别，关键点检测一张图也就这一个类别
        # 1.添加目标框的cx、cx、w、h
        ruler_points = np.array(temp_result.get("ruler"))
        x1, y1 = min(ruler_points[:, 0]), min(ruler_points[:, 1])
        x2, y2 = max(ruler_points[:, 0]), max(ruler_points[:, 1])
        center_x, center_y = (x1 + x2) / 2, (y1 + y2) / 2
        w, h = x2 - x1, y2 - y1
        result += [center_x / image_w, center_y / image_h, w / image_w, h / image_h]
        # 2.添加关键点，我们的关键点都是可见的，就不需要第三个是否可视的参数（一定注意关键点顺序）
        A_point = temp_result.get("A")[0]    # 拿到的是二维列表，里面就一个点，直接取出
        B_point = temp_result.get("B")[0]
        C_point = temp_result.get("C")[0]
        result += [A_point[0] / image_w, A_point[1] / image_h,
                   B_point[0] / image_w, B_point[1] / image_h,
                   C_point[0] / image_w, C_point[1] / image_h]
        str_result = " ".join(map(str, result))
        label_txt.write(str_result)
        label_txt.close()
        train_label.flush()
    train_label.close()


def labelme2yolo(labelme_path):
    """
    将labelme得到的json文件转成此yolo需要的annotation文件
    :param labelme_path: 所有labelme得到的标注文件的一个集合地址
    :param test_sie: 验证集所占的比例
    :return:
    """
    for name in ["images", "labels"]:
        if not os.path.exists(name):
            os.makedirs(name)

    all_files = os.listdir(labelme_path)
    all_files.sort(key=len)
    label_files = [file for file in all_files if file.split('.')[-1] == 'json']  # 一个元素是一个json文件的名字
    image_files = glob.glob(labelme_path + "/*.jpg")  # 列表，包含所有的图片，一个元素是一张图片的绝对地址

    train_files, val_files = train_test_split(label_files, test_size=0.1)
    print("train_n:", len(train_files), 'val_n:', len(val_files))

    # 读取json文件的内容，并将每张图的坐标归一化其写到对应的./label/*.txt文件
    load_json(train_files, 'train')
    load_json(val_files, 'val')
    print("标签已经处理完毕！")

    # 将图片复制到对应的./images目录下；这里的格式是将所有的图片放到./images下，然后通过train.txt、valid.txt、test.txt去取
    target_path = 'images'
    target_files = os.listdir(target_path)
    for image_file_path in tqdm(image_files, "图像复制中"):
        if os.path.split(image_file_path)[-1] in target_files:
            continue
        shutil.copy(image_file_path, target_path)
    print("Everything is OK!")


if __name__ == '__main__':
    start_time = time.time()
    json_path = r"./dataset/YBKC"
    labelme2yolo(json_path)
    end_time = time.time()
    print("总用时:{:.2f}分钟".format((end_time - start_time) / 60))
