"""
 仅仅是简单验证下转换后的格式对不对，就放这里做个参考了
"""

import os
import random
import PIL.ImageDraw as draw
import matplotlib.pyplot as plt
from PIL import Image

def main():
    """随机验证框位置是否正确"""
    image_path = r"./images"
    label_path = r"./labels"
    label_files = os.listdir(label_path)  # 所有标注文件.以标注为主，有的可能没目标

    random.shuffle(label_files)

    for label_name in label_files:
        image = Image.open(os.path.join(image_path, label_name.split('.')[0] + ".jpg"))
        image_w, image_h = image.size

        with open(os.path.join(label_path, label_name)) as f:
            lines = f.readlines()
            for line in lines:
                _center_x, _center_y, _w, _h = line.split(' ')[1:]
                center_x = float(_center_x) * image_w
                center_y = float(_center_y) * image_h
                w = float(_w) * image_w
                h = float(_h) * image_h
                x1 = center_x - (w / 2)
                y1 = center_y - (h / 2)
                x2 = x1 + w
                y2 = y1 + h
                temp = draw.Draw(image)
                temp.rectangle([x1, y1, x2, y2], outline='red', width=5)
        plt.imshow(image)
        plt.axis('off')
        plt.pause(1)


if __name__ == '__main__':
    main()
  
