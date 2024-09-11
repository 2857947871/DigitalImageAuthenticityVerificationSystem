import cv2
import numpy as np
from PIL import Image
from scipy.fftpack import dct
import matplotlib.pyplot as plt

def dct2(img):

    return cv2.dct(img.astype(np.float32))

def plot_dct_histogram(image_path):

    # 读取图像并转换为灰度图
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    if img is None:
        print("Error: Unable to read image.")
        return

    # 对图像进行 DCT 变换
    dct_transformed = dct2(img)

    # 平铺 DCT 系数并计算其绝对值
    dct_coeffs = np.abs(dct_transformed.flatten())

    # 绘制柱状图
    plt.figure(figsize=(10, 5))
    plt.hist(dct_coeffs, bins=50, log=True, color='blue', edgecolor='black')
    plt.title('Histogram of DCT Coefficients')
    plt.xlabel('DCT Coefficient Value')
    plt.ylabel('Frequency (log scale)')
    plt.grid(True)
    plt.savefig("D:/DeepLearning/Competition/DigitalImageAuthenticityVerificationSystem/result_plt/DCT.png")


if __name__ == "__main__":
    # 调用函数并传入图像路径
    image_path = "tools/123.jpg"
    plot_dct_histogram(image_path)
