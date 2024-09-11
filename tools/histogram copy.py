import cv2
import numpy as np
import matplotlib.pyplot as plt

def plot_color_histogram(image_path):
    # 读取图像
    image = cv2.imread(image_path)
    
    # 将图像从BGR转换为RGB
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # 分离图像的RGB通道
    channels = cv2.split(image)
    colors = ('r', 'g', 'b')
    channel_ids = (0, 1, 2)
    
    # 显示图例
    plt.title('Color Histogram')
    plt.xlabel('Pixel Value')
    plt.ylabel('Frequency')

    bins = np.arange(256)  # 0-255

    # 生成每个通道的直方图并绘制
    for (channel, color, channel_id) in zip(channels, colors, channel_ids):
        histogram = cv2.calcHist([image], [channel_id], None, [256], [0, 256]).flatten()
        plt.bar(bins, histogram, color=color, alpha=0.5, label=f'{color.upper()} channel')

    plt.grid(True)
    plt.savefig("D:/DeepLearning/Competition/DigitalImageAuthenticityVerificationSystem/result_plt/Color_Histogram.png")

if __name__ == "__main__":
    
    image_path = "tools/123.png"
    plot_color_histogram(image_path)



