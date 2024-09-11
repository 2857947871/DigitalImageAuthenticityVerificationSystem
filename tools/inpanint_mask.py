import cv2
import torch
import numpy as np


src = cv2.imread("tools/src.png")
mask = cv2.imread("tools/src_mask.png")

print(mask.shape)

for i in range(256):
    for j in range(384):
        for c in range(3):
            if mask[i][j][c] == 1:
                mask[i][j][c] = 0
            else:
                mask[i][j][c] = 1

dst = cv2.multiply(src, mask)

cv2.imwrite("tools/dst.png", dst)