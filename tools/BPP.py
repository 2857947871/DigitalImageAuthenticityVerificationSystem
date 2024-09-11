def calculate_bpp(image_mode, channel_depth):

    # 根据图像模式和通道深度计算BPP
    num_channels = len(image_mode) if image_mode != 'P' else 1  # 考虑调色板的情况
    bpp = num_channels * channel_depth
    
    return bpp

if __name__ == "__main__":

    # 示例图像信息
    image_mode = 'RGB'  # 图像模式：RGB
    channel_depth = 8   # 每个通道的位深度：8位

    # 计算BPP
    bpp = calculate_bpp(image_mode, channel_depth)

    # 打印结果
    print(f"图像模式：{image_mode}")
    print(f"每个通道的位深度：{channel_depth} bits")
    print(f"每像素位数(BPP): {bpp} bits/pixel")