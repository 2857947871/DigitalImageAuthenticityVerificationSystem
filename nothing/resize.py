import cv2

src = cv2.imread("result_samples/src0.png")
src = cv2.resize(src, dsize=(int(150), int(150)), interpolation=cv2.INTER_AREA)

cv2.imwrite("dst.jpg", src)