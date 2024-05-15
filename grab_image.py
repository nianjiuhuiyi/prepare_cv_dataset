"""
按空格同时抓取4个不同流的图像画面，并最终存为(1280, 1024)  # (w, h)的大小。
注意：
    要提前在此脚本路径中创建名为“images”的文件夹，
    且在images文件夹中再创建四个子文件夹，名字分别为“131”、“132”、“133”、“134”

如果没那么多路，自己看着改一下就好了。
------------------------------------------------------------------------------

下面再把单路的放这里，用的时候直接复制下面的代码就好了

import cv2
import time
from datetime import datetime
import os

def run(source, stride):
    cap = cv2.VideoCapture(source)
    assert cap.isOpened(), "Failed to open the video stream!"

    img_nums = 0

    n = 0
    while True:
        n += 1
        cap.grab()  # .read() = .grab() followed by .retrieve()
        if n % stride != 0:
            continue

        success, frame = cap.retrieve()
        if not success:
            print("读取失败，一分钟再次尝试...")
            time.sleep(60)
            cap.open(source)
            continue
        
        show_frame = cv2.resize(frame, (640, 480))
        cv2.imshow("135", show_frame)
        key = cv2.waitKey(1) & 0xFF
        if key == 32:   # 空格保存
            save_path = os.path.join(r"images", f"{img_nums:05d}.jpg")
            print(frame.shape)
            frame = cv2.resize(frame, (1280, 1024))
            cv2.imwrite(save_path, frame)
            print(img_nums, frame.shape,"\n")
            img_nums += 1
        elif key == ord('q') or key == 27:    # q或esc退出
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_stride = 1
    rtsp_path = r"rtsp://192.168.108.132:554/user=admin&password=&channel=1&stream=0.sdp?"
    run(rtsp_path, video_stride)
    
"""

import os
import cv2
import time
import queue
import threading
import numpy as np
from datetime import datetime

frame_size = (1280, 1024)  # (w, h)

g_Exit = False

def get_timestamp(only_time=False):
    now_time = datetime.now()
    if only_time:
        return now_time.strftime("%H:%M:%S")
    return now_time.strftime("%Y-%m-%d %H:%M:%S")


def get_image(video_path, que, video_stride=15):
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Failed to open the video stream: {}".format(video_path)

    # 当错误读取次数达到5次，认定为摄像头断开链接
    error_times = 0

    n = 0
    while True:
        cap.grab()  # .read() = .grab() followed by .retrieve()
        if n % video_stride != 0:
            continue
        success, frame = cap.retrieve()
        n += 1
        if success:
            h, w, c = frame.shape
            if h > w:
                frame = np.transpose(frame, (1, 0, 2))
            frame = cv2.resize(frame, frame_size)
            if que.full():
                que.get_nowait()
            que.put_nowait(frame)
        else:
            error_times += 1
            if error_times < 5:
                print("{}，错误次数：{}".format(get_timestamp(), error_times))
                continue
            # 5次数据获取失败，重连摄像头
            while True:
                ret = cap.open(video_path)
                if ret:
                    error_times = 0
                    break
                else:
                    print("{}, 摄像头读取失败，30秒后再次尝试...".format(get_timestamp()))
                    time.sleep(30)
        
        if g_Exit:
            break
    cap.release()


def run(source_side, source_behind, source_right, source_top=None, video_stride=15):
    # 侧面的图像数据队列
    que_side = queue.Queue(maxsize=2)
    thread_side = threading.Thread(target=get_image, args=(source_side, que_side, video_stride), daemon=True)
    # 后面的图像数据队列
    que_behind = queue.Queue(maxsize=2)
    thread_behind = threading.Thread(target=get_image, args=(source_behind, que_behind, video_stride), daemon=True)
    # 右侧相机队列
    que_right = queue.Queue(maxsize=2)
    thread_right = threading.Thread(target=get_image, args=(source_right, que_right, video_stride), daemon=True)

    # 顶部相机队列
    if source_top is not None:
        que_top= queue.Queue(maxsize=2)
        thread_top = threading.Thread(target=get_image, args=(source_top, que_top, video_stride), daemon=True)
        thread_top.start()

    # 开启取流线程
    thread_side.start()
    thread_behind.start()
    thread_right.start()
    time.sleep(1)

    img_nums = 0
    while True:
        im_side = que_side.get()
        im_behind = que_behind.get()
        im_right = que_right.get()

        if source_top is not None:
            im_top = que_top.get()
            show_top = cv2.resize(im_top, (640, 480))
            cv2.imshow("top", show_top)

        show_side = cv2.resize(im_side, (640, 480))
        show_behind = cv2.resize(im_behind, (640, 480))
        show_right = cv2.resize(im_right, (640, 480))

        # cv2.imshow("side", show_side)
        cv2.imshow("behind", show_behind)
        cv2.imshow("right", show_right)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:   # 空格保存
            save_path = os.path.join(r"images/131", f"{img_nums:05d}.jpg")
            cv2.imwrite(save_path, im_side)

            save_path = os.path.join(r"images/132", f"{img_nums:05d}.jpg")
            cv2.imwrite(save_path, im_behind)

            save_path = os.path.join(r"images/133", f"{img_nums:05d}.jpg")
            cv2.imwrite(save_path, im_right)
            
            if source_top is not None:
                save_path = os.path.join(r"images/134", f"{img_nums:05d}.jpg")
                cv2.imwrite(save_path, im_top)
                
            print(img_nums, im_side.shape,"\n")
            img_nums += 1
        elif key == ord('q') or key == 27:    # q或esc退出
            g_Exit = True
            break
    time.sleep(1)
    print("Done!")

if __name__ == '__main__':
    side = r"rtsp://192.168.108.131:554/user=admin&password=&channel=1&stream=0.sdp?"
    behind = r"rtsp://192.168.108.132:554/user=admin&password=&channel=1&stream=0.sdp?"
    right = r"rtsp://192.168.108.133:554/user=admin&password=&channel=1&stream=0.sdp?"
    top = r"rtsp://192.168.108.134:554/user=admin&password=&channel=1&stream=0.sdp?"
    run(source_side=side,
        source_behind=behind,
        source_right=right,
        source_top=top,
        video_stride=1
        )
