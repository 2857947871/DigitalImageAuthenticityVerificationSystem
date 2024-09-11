from PIL import Image

def get_image_mode(image_path):

    # 打开图像
    img = Image.open(image_path)

    # 获取图像模式
    mode = img.mode

    return mode