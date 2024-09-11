import cv2

ori = cv2.imread("result_inpainting/src.png")
mask = cv2.imread("result_inpainting/src_mask.png")

dst = ori * (1 - mask)

cv2.imwrite("result_inpainting/dst.png", dst)