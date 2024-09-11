import os
import cv2
import time

from tools.hash import file_sha1, file_sha256, file_sha512
from tools.PhotoShop_detect import photoshop_detect
from tools.MD5 import file_MD5
from tools.XMP import count_xmp_fields
from tools.image_mode import get_image_mode
from tools.channel_bit_depth import get_channel_bit_depth
from tools.BPP import calculate_bpp
from tools.Exif import extract_exif
from tools.JPEG import get_jpeg_quality_from_quantization_table


class BasicInformation:
    def __init__(self, file_path):

        self.file_path = file_path
        self.basic_information()
        
    def basic_information(self):

        self.image_file = cv2.imread(self.file_path)

        # 文件名称
        self.image_name = os.path.basename(self.file_path)

        # 文件路径
        self.image_path = os.path.dirname(self.file_path) 

        # 文件尺寸
        self.src_w_ori = self.image_file.shape[1]
        self.src_h_ori = self.image_file.shape[0]
        self.channel = self.image_file.shape[2]

        # 图像模式
        self.mode = get_image_mode(self.file_path)

        # 编码格式
        self.image_code = self.image_name.split('.')[-1]

        # 每通道位深度
        self.channel_bit_depth = get_channel_bit_depth(self.file_path)

        # BPP
        self.bpp = calculate_bpp(self.mode, self.channel_bit_depth)

        # hash
        self.hash_1 = file_sha1(self.file_path)
        self.hash_256 = file_sha256(self.file_path)
        self.hash_512 = file_sha512(self.file_path)

        # 获取文件的状态信息
        self.file_stat = os.stat(self.file_path)
        self.access_time = self.file_stat.st_atime
        self.create_time = self.file_stat.st_ctime

        # 修改时间
        self.formatted_access_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.access_time))

        # 创建时间
        self.formatted_create_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(self.create_time))

        # PS 字段
        self.photoshop_flag = photoshop_detect(self.file_path)

        # MD5
        self.md5 = file_MD5(self.file_path)

        # XMP 字段
        self.xmp_field_count = count_xmp_fields(self.file_path)

        # Exif 字段 & Markernote & IPTC
        self.exif_flag, self.Markernotes, self.iptc = extract_exif(self.file_path)

        # jpg 压缩质量因子
        self.quality = get_jpeg_quality_from_quantization_table(self.file_path)
    def show_information(self):

        self.information = []
        self.information.append('文件名称: ' + self.image_name)
        self.information.append('文件路径: ' + self.image_path)
        self.information.append('文件尺寸: ' + str(self.src_w_ori) + ' x ' + str(self.src_h_ori))
        self.information.append('通道数: ' + str(self.channel))
        self.information.append('图像模式: ' + self.mode)
        self.information.append('编码格式: ' + self.image_code)
        self.information.append('每通道位深度: ' + str(self.channel_bit_depth))
        self.information.append('BPP: ' + str(self.bpp))
        self.information.append('SHA1: ' + self.hash_1)
        self.information.append('SHA256: ' + self.hash_256)
        self.information.append('SHA512: ' + self.hash_512)
        self.information.append('访问时间: ' + self.formatted_access_time)
        self.information.append('创建时间: ' + self.formatted_create_time)
        self.information.append('PS字段: ' + str(self.photoshop_flag))
        self.information.append('MD5: ' + self.md5)
        self.information.append('XMP字段: ' + str(self.xmp_field_count))
        self.information.append('Exif字段: ' + str(self.exif_flag))
        self.information.append('Markernotes字段: ' + str(self.Markernotes))
        self.information.append('IPTC字段: ' + str(self.iptc))
        self.information.append('JPEG压缩质量因子: ' + str(self.quality))

        return self.information

if __name__ == '__main__':

    BI = BasicInformation('tools/00006_fake.jpg')
    print(BI.show_information())