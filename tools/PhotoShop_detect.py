from PIL import Image

def photoshop_detect(image_path):

    # 打开图像文件
    img = Image.open(image_path)

    # 获取图像的元数据
    metadata = img.info

    # 检查元数据中是否包含 Photoshop 处理软件信息
    if 'Photoshop' in metadata:
        flag = 1
    else:
        flag = 0

    return flag