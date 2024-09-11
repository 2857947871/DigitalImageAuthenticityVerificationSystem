from PIL import Image

def extract_exif(image_path):

    img = Image.open(image_path)
    exif_flag = None
    maker_notes = None
    iptc =  None
    # 获取 Exif 数据
    exif_data = img.getexif()
    print(exif_data)

    if exif_data is not None:
        exif_flag = 1
        if 37500 in exif_data:
            # 提取 MakerNotes
            maker_notes = exif_data[37500]
        if 33723 in exif_data:
            # 提取 IPTC 信息
            iptc = exif_data[33723]

    return exif_flag, maker_notes, iptc

# 调用函数并传入图像路径
if __name__ == "__main__":

    image_path = "tools/20240515225748.jpg"
    print(extract_exif(image_path))
