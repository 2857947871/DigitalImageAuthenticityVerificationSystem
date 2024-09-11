from PIL import Image

def get_channel_bit_depth(image_path):

    # 打开图像
    img = Image.open(image_path)

    bit_depth = img.getextrema()[0][1].bit_length()
    
    return bit_depth