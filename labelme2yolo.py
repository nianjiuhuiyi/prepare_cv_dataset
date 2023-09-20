import time
import os
import shutil
import json
import numpy as np
from sklearn.model_selection import train_test_split
import glob
from tqdm import tqdm
np.random.seed(41)       # 为train_test_split设一个随机种子，保证每次运行都结果一致

keys = dict(
    开口扳手='0',
    扭矩扳手正='1',
    扭矩扳手反='2',
    扭矩扳手带套筒='3',
    套筒扳手正='4',
    套筒扳手反='5',
    套筒扳手带套筒='6',
    分流导线='7',
    平锉刀='8',
    游标卡尺='9',
    万用表='10',
    套筒='11',
    受电弓弓头='12',
    手='13',
    钳子='14',
    螺丝刀='15',
    手锤='16',
    美工刀='17',
    手锯='18',
    卷尺='19',
    钢直尺='20',
    油漆笔='21',
    导电膏='22',
    碳滑条='23',
    螺母='24',
    螺栓='25',
    万用表表笔='26'
)


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
        train_label.write("data/custom/images/{}.jpg\n".format(train_file.split('.')[0]))

        classes_list = data['shapes']  # a list（一个元素是一个物品）
        label_txt = open(os.path.join('./labels', train_file.split('.')[0] + '.txt'), 'w')
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


def labelme2yolo(labelme_path):
    """
    将labelme得到的json文件转成此yolo需要的annotation文件
    :param labelme_path: 所有labelme得到的标注文件的一个集合地址
    :param test_sie: 验证集所占的比例
    :return:
    """
    all_files = os.listdir(labelme_path)
    label_files = [file for file in all_files if file.split('.')[-1] == 'json']  # 一个元素是一个json文件的名字
    image_files = glob.glob(labelme_path + "/*.jpg")  # 列表，包含所有的图片，一个元素是一张图片的绝对地址

    train_files, test_val_files = train_test_split(label_files, test_size=0.15)
    test_files, val_files = train_test_split(test_val_files, test_size=0.15)
    print("train_n:", len(train_files), 'test_n:', len(test_files), 'val_n:', len(val_files))

    # "errors.txt是没有标注的json文件的名称，一般用不上，暂时先放这里，后面删除"
    # with open("errors.txt") as f:
    #     datas = f.readlines()
    # print(datas)
    # for data in datas:
    #     data = data.replace('\n', '')
    #     if data in train_files:
    #         train_files.remove(data)
    #     elif data in test_files:
    #         test_files.remove(data)
    #     else:
    #         val_files.remove(data)
    # print("train_n:", len(train_files), 'test_n:', len(test_files), 'val_n:', len(val_files))


    # 读取json文件的内容，并将每张图的坐标归一化其写到对应的./label/*.txt文件
    load_json(train_files, 'train')
    load_json(test_files, 'test')
    load_json(val_files, 'valid')
    print("标签已经处理完毕！")

    # 将图片复制到对应的./images目录下；这里的格式是将所有的图片放到./images下，然后通过train.txt、valid.txt、test.txt去取
    target_path = './images'
    target_files = os.listdir(target_path)
    for image_file_path in tqdm(image_files, "图像复制中"):
        if os.path.split(image_file_path)[-1] in target_files:
            continue
        shutil.copy(image_file_path, target_path)
    print("Everything is OK!")


if __name__ == '__main__':
    start_time = time.time()
    json_path = r"./data_two_fuse"
    labelme2yolo(json_path)
    end_time = time.time()
    print("总用时:{:.2f}分钟".format((end_time - start_time) / 60))
