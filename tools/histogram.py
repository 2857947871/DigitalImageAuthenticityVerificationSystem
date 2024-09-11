import cv2
import matplotlib.pyplot as plt
import numpy as np

def plot_color_histogram(image_path):
    # 读取图像
    img = cv2.imread(image_path)
    
    if img is None:
        print("Error: Unable to read image.")
        return

    # 分离图像的RGB通道
    channels = cv2.split(img)
    colors = ('b', 'g', 'r')
    channel_ids = (0, 1, 2)

    # 创建一个直方图
    plt.figure(figsize=(10, 5))
    bins = np.arange(256)  # 0-255

    # 生成每个通道的直方图并绘制
    for (channel, color, channel_id) in zip(channels, colors, channel_ids):
        histogram = cv2.calcHist([img], [channel_id], None, [256], [0, 256]).flatten()
        plt.bar(bins, histogram, color=color, alpha=0.5, label=f'{color.upper()} channel')

    # 设置标题和标签
    plt.title('Color Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')
    plt.legend()
    plt.grid(True)

    # 保存图像
    plt.savefig("D:/DeepLearning/Competition/DigitalImageAuthenticityVerificationSystem/result_plt/Color_Histogram.png")


if __name__ == "__main__":
    image_path = "tools/123.png"
    plot_color_histogram(image_path)