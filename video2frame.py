import os
import time
import tqdm

import cv2
import numpy as np

video_dir = r"videos"
img_save_dir = r"images"
if not os.path.exists(img_save_dir):
    os.makedirs(img_save_dir, exist_ok=True)


frame_size = (1280, 1024)     # (w, h)


if __name__ == '__main__':
    counts = 0
    for video_name in tqdm.tqdm(os.listdir(video_dir), desc="进度"):
        video_path = os.path.join(video_dir, video_name)
        cap = cv2.VideoCapture(video_path)
        nums = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            h, w, c = frame.shape
            # 一定这样去判一下，确保竖屏拍摄的也是OK的。
            if h > w:
                frame = np.transpose(frame, (1, 0, 2))
            assert frame.shape == (1080, 1920, 3)
            result_frame = cv2.resize(frame, frame_size)
            # print(f"original_shape: {frame.shape} ", f"now_shape: {result_frame.shape}")
            nums += 1
            if (nums % 15 == 0) and (nums % 10 != 0):
                name = round(time.time() * 1000)
                save_path = os.path.join(img_save_dir, f"{name}.jpg")
                cv2.imwrite(save_path, result_frame)
                counts += 1
                # print("counts: {}".format(counts))

            # cv2.imshow("demo", frame)
            # cv2.imshow("res", result_frame)
            # if cv2.waitKey(0) & 0xFF != 255:
            #     exit(0)
            #     break
            # 
        cap.release()
    # cv2.destroyAllWindows()
    time.sleep(0.5)
    print("Done! ", "总的数量：{}".format(counts))






