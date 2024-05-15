"""
功能：
    把目标沿其轮廓或是最小外接矩形从原图中抠出来，并贴到一个纯黑或纯白的背景中。

注意：
    以下代码背景是读取coco格式的标注文件，然后把游标卡尺、斜度塞尺抠出来，
    现在可能用不到了，但其核心代码是通用的，有这个需求时，拿来很简单就能改出来。

"""

import json
import os
import cv2
import numpy as np
from tqdm import tqdm


def min_index(arr1, arr2):
    """Find a pair of indexes with the shortest distance.
    Args:
        arr1: (N, 2).
        arr2: (M, 2).
    Return:
        a pair of indexes(tuple).
    """
    dis = ((arr1[:, None, :] - arr2[None, :, :]) ** 2).sum(-1)
    return np.unravel_index(np.argmin(dis, axis=None), dis.shape)


def merge_multi_segment(segments):
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
        idx1, idx2 = min_index(segments[i - 1], segments[i])
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


if __name__ == '__main__':

    # 背景图是最小外接矩形，False的话就是用的轮廓
    is_minBox = True

    with open("annotations.json", 'r', encoding="utf-8") as fp:
        data = json.load(fp)

    # 得到已有的图片的{id: file_name},得到di对应的图片对应的图片路径
    file_path_dict = {item.get("id"): item.get("file_name") for item in data.get("images")}

    annotations = data.get("annotations")
    for annotation in tqdm(annotations, desc="进度: "):
        category_id = annotation.get("category_id")
        if category_id == 0:  # 扭矩扳手不管
            continue

        image_id = annotation.get("image_id")
        img_path = file_path_dict.get(image_id)
        img = cv2.imread(img_path)
        img_name = os.path.basename(img_path)

        segmentation = annotation.get("segmentation")
        # 会有分割区域是多个部分的，即 segmentation 是 [[]] ，大多数情况 len(segmentation) = 1,所以以前常直接segmentation[0]
        # 现在不为区域个数不为1时就要合并，方法是来自yolov5的官方：https://github.com/ultralytics/JSON2YOLO/blob/c38a43f342428849c75c103c6d060012a83b5392/general_json2yolo.py#L295
        if len(segmentation) > 1:
            # 合并的方法
            segmentation = merge_multi_segment(segmentation)
            segmentation = np.concatenate(segmentation, axis=0).reshape(-1).tolist()
        else:
            segmentation = segmentation[0]

        contour = np.intp(segmentation)
        contour = contour.reshape(-1, 2)

        if is_minBox:
            min_rect = cv2.minAreaRect(contour)
            box = cv2.boxPoints(min_rect)
            contour = np.intp(box)

        # 做一个纯黑的背景,把分割目标割出来(可以以最小外接矩形，也可是以直接的分割结果)
        black_canvas = np.zeros_like(img)
        cv2.drawContours(image=black_canvas, contours=[contour], contourIdx=0, color=(255, 255, 255), thickness=-1)
        black_canvas = cv2.cvtColor(black_canvas, cv2.COLOR_BGR2GRAY)
        img_result = cv2.bitwise_and(img, img, mask=black_canvas)

        save_path = ""
        if category_id == 1:  # 游标卡尺
            save_path = os.path.join("YBKC", img_name)
        elif category_id == 2:  # 斜度塞尺
            save_path = os.path.join("XDSC", img_name)

        if save_path:
            cv2.imwrite(save_path, img_result)

    print("Done!")
