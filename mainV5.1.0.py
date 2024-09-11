import os
import sys
import cv2
import time
import torch
import shutil
import numpy as np
from datetime import datetime
from threading import Thread
from torchvision.transforms import ToTensor
from PyQt5.QtGui import QImage, QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QTimer, QThread, QBasicTimer, \
    pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QFileDialog, QInputDialog,\
    QHBoxLayout, QVBoxLayout,\
    QLabel, QTextBrowser, QMessageBox, QPushButton, QSlider, QAction,\
    QComboBox, QProgressBar

from basic_information import BasicInformation
from tools.DCT import plot_dct_histogram
from tools.histogram import plot_color_histogram

# 获取当前脚本的路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 构建要导入的模块的路径
TurFor_path = os.path.join(current_dir, 'TurFor')
GAN_datection_path = os.path.join(current_dir, 'GANImageDetection')
LaMa_module_path = os.path.join(current_dir, 'LaMa')
Painter_path = os.path.join(current_dir, 'Painter')
Super_resolution_path = os.path.join(current_dir, 'SuperResolution')
DeBlur_path = os.path.join(current_dir, 'HI_Diff')
DeNoise_path = os.path.join(current_dir, 'MPRNet')
DeWeather_path = os.path.join(current_dir, 'IRDM')

# 将模块路径添加到系统路径中
sys.path.append(GAN_datection_path)
sys.path.append(LaMa_module_path)
sys.path.append(Painter_path)
sys.path.append(Super_resolution_path)
sys.path.append(DeBlur_path)
sys.path.append(DeNoise_path)
sys.path.append(DeWeather_path)

from TruFor.src.trufor_test import trufor_datect
from GANImageDetection.gan_vs_real_detector import GAN_Detector
from LaMa.bin.predict import main
LaMa_inpainting = main
from Painter.option import painter_args
from Painter.painter import Sketcher
from SuperResolution import bsrgan_sr
from HI_Diff import deblur
from MPRNet import denoise
from IRDM import deweather


def postprocess(image):

    image = torch.clamp(image, -1., 1.)
    image = (image + 1) / 2.0 * 255.0
    image = image.permute(1, 2, 0)
    image = image.cpu().numpy().astype(np.uint8)
    return image


class WorkerThread(QThread):
    # 定义一个信号，用于发送进度更新
    progress_updated = pyqtSignal(int)
    
    def  __init__(self, speed=None):
        # speed 越小, 更新越快
        super().__init__()
        self.speed = speed

    def run(self):
        speed = self.speed
        # 模拟一个耗时任务，任务完成后发送信号更新进度条
        for i in range(101):
            if win.my_thread.is_alive() == False:
                speed = 0.00001
            self.speed = speed
            self.progress_updated.emit(i) # 发送进度更新信号
            time.sleep(self.speed)


class ClickableLabel_dst(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        
    def resize_window(self, new_size_w, new_size_h):
        cv2.namedWindow('dst', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('dst', new_size_w, new_size_h)

    def mousePressEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            try:
                cv2.namedWindow('dst', cv2.WINDOW_NORMAL)
                dst = cv2.imread("result_show/dst.png")
                while True:
                    cv2.imshow('dst', dst)
                    cv2.setMouseCallback('dst', lambda event, x, y, flags, param: self.mouse_scroll(event, flags))
                    k = cv2.waitKey(1) & 0xFF
                    if k == 27:  # 按下ESC键退出
                        cv2.destroyAllWindows()
                        break
            except:
                pass

    def mouse_scroll(self, event, flags):
        if event == cv2.EVENT_MOUSEWHEEL:
            print(cv2.getWindowImageRect('dst'))
            current_size_w = cv2.getWindowImageRect('dst')[2]
            current_size_h = cv2.getWindowImageRect('dst')[3]
            
            if flags > 0:  # 滚轮向上滚动，增加窗口大小
                new_size_w = min(current_size_w + 10, 2000)
                new_size_h = min(current_size_h + 10, 2000)
            else:  # 滚轮向下滚动，减小窗口大小
                new_size_w = max(current_size_w - 10, 100)
                new_size_h = max(current_size_h - 10, 100)
            self.resize_window(new_size_w, new_size_h)


class my_window(QMainWindow):

    def __init__(self):

        super().__init__()
        
        # 变量初始化
        self.my_thread = None
        self.src_image = None

        self.sr_flag = None
        self.dct_flag = None
        self.deblur_flag = None
        self.detect_flag = None
        self.denoise_flag = None
        self.deweather_flag = None
        self.histogram_flag = None
        self.slider_sr_flag = None
        self.inpainting_flag = None
        self.detect_gan_flag = None

        self.score = 0
        self.conf = 0.6
        self.sr_scale = 2
        self.src_w_ori = 0
        self.src_h_ori = 0

        self.samples_num_history = []
        self.results_dir = ["result_sr", "result_tmp", "result_deblur", "result_inpainting", "result_denoise", "result_deweather", \
                    "result_plt", "result_show", "result_samples"] 
        self.results_samples = ["result_0", "result_1", "result_2", "result_3", "result_4", "result_5"]

        self.images_names = []
        self.result_image = ['result_tmp/src_ori.png', 'result_plt/Color_Histogram.png', 'result_plt/DCT.png', 'result_tmp/dst.png', 'result_tmp/conf_prob.png', 'result_tmp/heatmap.png', 'result_tmp/npp_prob.png',\
            'result_denoise/dst.png', 'result_sr/dst.png', 'result_tmp/result_inpainting.jpg', 'result_deweather/dst.png', 'result_deblur/dst.png']
        self.function = ["原图", "颜色直方图", "DCT变换直方图", "篡改区域定位图", "置信图", "热度图", "噪声指纹", "图像去噪", "图像超分辨率", "图像修复", "图像去雨/雪/雾", "图像去运动模糊"]

        # widget 初始化
        # 检材区
        self.sample0, self.sample1, self.sample2, self.sample3, self.sample4  = [None] * 5
        self.samples = [self.sample0, self.sample1, self.sample2, self.sample3, self.sample4]

        # 功能区
        self.functionLayoutLabel_detection, self.btn1, self.btn2, self.btn3, self.btn4, self.btn5, \
            self.functionLayoutLabel_enhance, self.btn6, self.btn7, self.btn8, self.btn9, self.btn10 = [None] * 12
        self.btns = [self.functionLayoutLabel_detection, self.btn1, self.btn2, self.btn3, self.btn4, self.btn5, \
            self.functionLayoutLabel_enhance, self.btn6, self.btn7, self.btn8, self.btn9, self.btn10]
        self.btn_label = ["图像真实性鉴定", "●图像基本信息", "●DCT直方图", "●颜色直方图", "●生成式图像检测", "●篡改鉴定及定位", \
            "图像处理", "●图像修复", "●超分辨率", "●图像去模糊", "●图像去噪", "●去雨/雪/雾"]

        # log文件初始化
        self.current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        with open(f"logs/log_{self.current_time}.txt", "a", encoding='utf-8') as f:
            f.write(f"历史操作记录\n系统启动:{self.current_time} \n")

        # GUI初始化
        self.ui_init()
        self.ui_init_image()

        # 绑定信号与槽
        self.open_action.triggered.connect(self.openFile)
        self.save_image_action.triggered.connect(self.saveImageFile)
        self.save_logs_action.triggered.connect(self.saveLogFile)
        self.quit_action.triggered.connect(self.quit)

        # 清除历史缓存
        self.clear(which="all")

    def ui_init(self):
        
        """==================================================================== 字体大小 初始化===================================================================="""
        font_btn = QFont("Arial", 16)
        font_path = QFont("Arial", 14)
        font_label = QFont("Arial", 20)

        """==================================================================== menu 初始化===================================================================="""
        # 设置菜单栏
        self.resize(2560, 1440)
        self.font = QFont("Arial", 20)
        self.setWindowTitle("Digital Image Authenticity Verification System")
        menu = self.menuBar()
        menu.setStyleSheet("QMenuBar {font-size: 22px;background-color: lightblue;}")
        file_menu = menu.addMenu("文件")
        file_menu.setStyleSheet('font-size: 20px;')
        quit_menu = menu.addMenu("退出")
        quit_menu.setStyleSheet('font-size: 20px;')

        # 创建动作
        self.open_action = QAction("打开", self)
        self.save_image_action = QAction("导出结果图像", self)
        self.save_logs_action = QAction("导出历史记录", self)
        self.quit_action = QAction("退出", self)

        # 将动作添加到文件菜单
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_image_action)
        file_menu.addAction(self.save_logs_action)
        quit_menu.addAction(self.quit_action)

        # central Widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)

        # central Widget 里面的 主 layout
        self.mainLayout = QHBoxLayout(centralWidget)

        """==================================================================== 检材区 初始化===================================================================="""
        # 暂时没有图像，等打开图像后更新
        self.sampleArea = QVBoxLayout()
        self.samples_label = QLabel("检材区", self)
        
        self.samples_label = self.widget_init(widget=self.samples_label, widget_class='label', width=150, height=30, \
            border='2px solid #D7E2F9', background_color='lightblue', font=font_path)
        self.sampleArea.addWidget(self.samples_label)
        
        for i in range(len(self.samples)):
            self.samples[i] = QPushButton(self)
            self.samples[i].setMinimumSize(150, 150)
            self.samples[i].setStyleSheet('border:2px solid #D7E2F9;')
            self.samples[i].clicked.connect(lambda checked, i=i: self.which_sample_clicked(sample_num=i))
            self.sampleArea.addWidget(self.samples[i])
        self.sampleArea.addStretch()

        """==================================================================== 功能区 初始化===================================================================="""
        self.functionLayout = QVBoxLayout()
        self.function_label = QLabel("功能区", self)
        self.btn_function = [None, self.image_information, self.dct, self.histogram, self.GanDetection, self.detect, \
            None, self.inpainting_by_myself, self.super_resolution, self.deblur, self.denoise, self.deweather]

        self.function_label = self.widget_init(widget=self.function_label, widget_class='label', width=150, height=30, \
            border='2px solid #D7E2F9', background_color='lightblue', font=font_path)
        self.functionLayout.addWidget(self.function_label)
        
        for i in range(len(self.btns)):
            if i % 6 == 0: # 功能区label
                self.btns[i] = QLabel(self.btn_label[i], self)
                self.btns[i] = self.widget_init(widget=self.btns[i], widget_class='label', width=150, height=50, \
                    border='2px solid #D7E2F9', background_color='lightblue', font=font_label, font_weight='bold')
            else: # 功能区button
                self.btns[i] = QPushButton(self.btn_label[i], self)
                self.btns[i] = self.widget_init(widget=self.btns[i], widget_class='button', width=250, height=50, font=font_btn)
                self.btns[i].clicked.connect(self.btn_function[i])
            if i == 6:
                self.functionLayout.addStretch(1)
            self.functionLayout.addWidget(self.btns[i])
        self.functionLayout.addStretch(2)

        """==================================================================== src区 初始化===================================================================="""
        self.srcLayout = QVBoxLayout()
        self.sliderLayout = QVBoxLayout()
        self.progressBarLayout = QVBoxLayout()
        
        self.label_src_path = QLabel("证据图像:", self)
        self.label_src_path = self.widget_init(widget=self.label_src_path, widget_class='label', width=800, height=30, \
            border='2px solid #D7E2F9', background_color='lightblue', font=font_path)
        
        self.label_src_img = QLabel(self)
        self.label_src_img = self.widget_init(widget=self.label_src_img, widget_class='label', width=800, height=800, \
            border='2px solid #D7E2F9', background_color='None', font=font_label)

        self.progress_bar_title = QLabel("实时进度条", self)

        self.progress_bar_title = self.widget_init(widget=self.progress_bar_title, widget_class='label', width=100, height=80, \
            border='2px solid #D7E2F9', font=font_label)

        self.progress_bar = QProgressBar(self)
        self.progress_bar = self.widget_init(widget=self.progress_bar, widget_class='bar', width=800, border='2px solid #D7E2F9')

        self.slider_1 = QSlider(Qt.Horizontal, self)
        self.slider_1 = self.widget_init(widget=self.slider_1, widget_class='slider', width=800, border='2px solid #D7E2F9')

        self.slider_label_title = QLabel("默认置信度: 0.6", self)
        self.slider_label_title = self.widget_init(widget=self.slider_label_title, widget_class='label', width=100, height=80, \
            border='2px solid #D7E2F9', font=font_label)

        self.progressBarLayout.addWidget(self.progress_bar_title)
        self.progressBarLayout.addWidget(self.progress_bar)

        self.sliderLayout.addWidget(self.slider_label_title)
        self.sliderLayout.addWidget(self.slider_1)
        self.sliderLayout.addStretch(1)
        self.sliderLayout.addLayout(self.progressBarLayout)
        self.sliderLayout.addStretch(2)

        self.srcLayout.addWidget(self.label_src_path)
        self.srcLayout.addWidget(self.label_src_img)
        self.srcLayout.addLayout(self.sliderLayout)
        
        """==================================================================== 历史记录区 初始化===================================================================="""
        self.historyLayout = QVBoxLayout()
        self.historyText = QTextBrowser(self)
        self.history_label = QLabel("历史操作记录", self)
        
        self.history_label.setFont(font_path)
        self.history_label.setMinimumHeight(30) # 指定 label 大小
        self.history_label.setStyleSheet('border:2px solid #D7E2F9;background-color: None;')
        self.history_label = self.widget_init(widget=self.history_label, widget_class='label', width=300, height=30, \
            border='2px solid #D7E2F9', background_color='lightblue', font=font_path)

        self.historyText.setFont(font_path)
        self.historyText.setStyleSheet('border:2px solid #D7E2F9;')

        self.historyLayout.addWidget(self.history_label)
        self.historyLayout.addWidget(self.historyText)

        self.mainLayout.addLayout(self.sampleArea)
        self.mainLayout.addLayout(self.functionLayout)
        self.mainLayout.addLayout(self.srcLayout)

    def ui_init_image(self):

        """====================================================================dst区 初始化===================================================================="""
        font_path = QFont("Arial", 14)
        font_label = QFont("Arial", 20)
        
        self.dstLayout = QVBoxLayout()
        self.historyLayout = QVBoxLayout()
        
        self.historyText.setFont(font_label)
        self.historyText.setStyleSheet('border:2px solid #D7E2F9;')
        
        self.label_dst_path = QLabel("结果图像:", self)
        self.label_dst_path = self.widget_init(widget=self.label_dst_path, widget_class='label', width=800, height=30, \
            border='2px solid #D7E2F9', background_color='lightblue', font=font_path)
        
        self.label_dst_img = ClickableLabel_dst(self)
        self.label_dst_img = self.widget_init(widget=self.label_dst_img, widget_class='label', width=800, height=800, border='2px solid #D7E2F9', font=font_label)

        self.textLog = QTextBrowser(self)
        self.textLog.setFont(font_label)
        self.textLog.setStyleSheet('border:2px solid #D7E2F9;') # 设定边界
        
        self.historyLayout.addWidget(self.history_label)
        self.historyLayout.addWidget(self.historyText)
        self.dstLayout.addWidget(self.label_dst_path)
        self.dstLayout.addWidget(self.label_dst_img)
        self.dstLayout.addWidget(self.textLog)

        # 添加至主界面
        self.mainLayout.addLayout(self.dstLayout)
        self.mainLayout.addLayout(self.historyLayout)

    def ui_init_no_image(self):

        """====================================================================dst区 初始化===================================================================="""
        self.dstLayout = QVBoxLayout()
        self.historyLayout = QVBoxLayout()
        
        self.historyText.setFont(self.font)
        self.historyText.setStyleSheet('border:2px solid #D7E2F9;')

        self.historyLayout.addWidget(self.history_label)
        self.historyLayout.addWidget(self.historyText)
        
        self.textLog = QTextBrowser(self)
        self.textLog.setFont(self.font)
        self.textLog.setStyleSheet('border:2px solid #D7E2F9;') # 设定边界

        self.dstLayout.addWidget(self.textLog)

        # 添加至主界面
        self.mainLayout.addLayout(self.dstLayout)
        self.mainLayout.addLayout(self.historyLayout)

    def widget_init(self, widget, widget_class=None, width=None, height=None, border=None, background_color=None, font=None, font_weight=None):
        
        if widget_class == 'label':
            if width or height:
                widget.setMinimumSize(width, height)
            widget.setStyleSheet(f'border:{border};background-color:{background_color};font-weight:{font_weight};text-align: left;padding-left: 10px;')
            widget.setFont(font)
        elif widget_class == 'button':
            if width or height:
                widget.setMinimumSize(width, height)
            widget.setStyleSheet(f'text-align: left;padding-left: 10px;')
            widget.setFont(font)
        elif widget_class == 'slider':
            widget.setRange(20, 100)
            if width or height:
                widget.setFixedWidth(width)
            widget.setStyleSheet(f'border:{border};')
        elif widget_class == 'bar':
            widget.setStyleSheet(f'border:{border};')

        return widget

    def slider_value_get(self, value=60):

        self.conf = value / 100
        self.slider_label_title.setFont(self.font)
        self.slider_label_title.setText(f"置信度: {self.conf}")

    def openFile(self):

        self.clear(which="all")

        try:
            self.slider_1.valueChanged.disconnect(self.img_switch)
        except:
            pass
        self.slider_1.setRange(20, 100) # 取值范围
        self.slider_label_title.setFont(self.font)
        self.slider_label_title.setText(f"置信度: {self.conf}")
        self.slider_1.valueChanged.connect(self.slider_value_get)
        
        options = QFileDialog.Options()
        self.image_files, _ = QFileDialog.getOpenFileNames(self, "Open Images", "", "Images (*.png *.xpm *.jpg *.bmp)", options=options)
        if self.image_files:
            self.history_show(f"打开图片: \n")
            i = 0
            try:
                for image in self.image_files:
                    self.history_show(f"{image}\n")
                    # 记录原始路径
                    self.images_names.append(image)
                    # 重新缓存
                    self.image_name = image.split("/")[-1]
                    image_tmp = cv2.imread(image)
                    cv2.imwrite(f"result_samples/src{i}.png", image_tmp)
                    image_tmp = cv2.resize(image_tmp, (140, 140))
                    cv2.imwrite(f"result_samples/src{i}_sample.png", image_tmp)
                    i += 1
            except:
                self.textLog.setText("最多支持选择5张图片,请重新选择")

            for i in range(len(self.image_files)):
                self.samples[i].setIcon(QIcon(f"result_samples/src{i}.png"))
                self.samples[i].setIconSize(self.samples[i].size())
        
        # 检材区图片缓存到各自专属文件夹
        for i in range(len(self.image_files)):
            for j in range(len(self.results_dir)):
                if self.results_dir[j] == "result_deweather":
                    shutil.copyfile(f"result_samples/src{i}.png", os.path.join(self.results_samples[i], self.results_dir[j], "input", "src.png"))
                    shutil.copyfile(f"result_samples/src{i}.png", os.path.join(self.results_samples[i], self.results_dir[j], "target", "src.png"))
                shutil.copyfile(f"result_samples/src{i}.png", os.path.join(self.results_samples[i], self.results_dir[j], "src.png"))

    def saveImageFile(self):

        self.filename, _ = QFileDialog.getSaveFileName(
                self, 
                "保存图片", 
                ".", 
                "图像文件(*.png *.jpg)")

        if self.filename:
            self.dst_image = cv2.cvtColor(self.dst_image, cv2.COLOR_BGR2RGB)
            cv2.imwrite(self.filename, self.dst_image)

        self.history_show(f"保存图片: {self.filename}\n")
        self.textLog.setText("保存成功!")

    def saveLogFile(self):
            
            self.filename, _ = QFileDialog.getSaveFileName(
                    self, 
                    "保存日志", 
                    ".", 
                    "文本文件(*.txt)")
    
            if self.filename:
                shutil.copyfile(f"logs/log_{self.current_time}.txt", self.filename)
    
            self.history_show(f"保存日志: {self.filename}\n")
            self.textLog.setText("保存成功!")

    def image_information(self):
        try:
            self.clear_layout()
            self.ui_init_no_image()

            BI = BasicInformation(file_path="result_tmp/src_ori.png")
            self.src_w_ori = BI.src_w_ori
            self.src_h_ori = BI.src_h_ori

            # 显示信息
            font = QFont("Arial", 16)
            self.textLog.setFont(font)
            self.textLog.setText(f'文件名称: {BI.image_name}\n')
            self.textLog.append(f'文件路径: {BI.image_path}\n')
            self.textLog.append(f'MD5: {BI.md5}\n')
            self.textLog.append(f'编码格式: {BI.image_code}\n')
            self.textLog.append(f'文件尺寸: {BI.src_w_ori} * {BI.src_h_ori}\n')
            self.textLog.append(f'通道数: {BI.channel}\n')
            self.textLog.append(f'图像模式: {BI.mode}\n')
            self.textLog.append(f'每通道位深度: {BI.channel_bit_depth}\n')
            self.textLog.append(f'BPP: {BI.bpp}\n')
            self.textLog.append(f'Exif 字段: {BI.exif_flag}\n')
            self.textLog.append(f'Makernotes 字段: {BI.Markernotes}\n')
            self.textLog.append(f'IPTC 字段: {BI.iptc}\n')
            self.textLog.append(f'XMP 字段: {BI.xmp_field_count}\n')
            self.textLog.append(f'PS 字段: {BI.photoshop_flag}\n')
            self.textLog.append(f'访问时间: {BI.formatted_access_time}\n')
            self.textLog.append(f'创建时间: {BI.formatted_create_time}\n')
            self.textLog.append(f'hash_1: {BI.hash_1}\n')
            self.textLog.append(f'hash_256: {BI.hash_256}\n')
            self.textLog.append(f'hash_512: {BI.hash_512}\n')
            self.textLog.append(f'JPEG 质量因子: {BI.quality}\n')
            self.history_show(f"{self.images_names[self.sample_num]} 基本信息展示\n")
        except:
            self.textLog.setText("请先打开图片或在检材区选择图片")

    def dct(self):

        self.clear_layout()
        self.ui_init_image()
        
        self.my_thread = Thread(target=plot_dct_histogram(image_path="result_tmp/src_ori.png"), daemon=True)
        self.my_thread.start()
        self.dct_flag = True
        self.startTask(speed=0.02)

    def histogram(self):

        self.clear_layout()
        self.ui_init_image()
        
        self.my_thread = Thread(target=plot_color_histogram(image_path="result_tmp/src_ori.png"), daemon=True)
        self.my_thread.start()
        self.histogram_flag = True
        self.startTask(speed=0.02)

    def detect(self):

        self.clear_layout()
        self.ui_init_image()

        # 分辨率调整, 防止爆显存
        self.src_detection = cv2.imread("./result_tmp/src_ori.png")
        if self.src_detection.shape[0] > 512 or self.src_detection.shape[1] > 512:
            self.src_detection = cv2.resize(self.src_detection, (int(self.src_detection.shape[1]/2), int(self.src_detection.shape[0]/2)))
            cv2.imwrite("result_tmp\src_detection.png", self.src_detection)
            self.textLog.setText(f'为防止爆显存, 将其调整为 {int(self.src_detection.shape[1]), int(self.src_detection.shape[0])}')
            self.textLog.setText("正在篡改鉴定及定位,请稍等...")
        else:
            cv2.imwrite("result_tmp\src_detection.png", self.src_detection)
            self.textLog.setText("正在篡改鉴定及定位,请稍等...")

        self.my_thread = Thread(target=self.ManipulationDetection, daemon=True)
        self.my_thread.start()
        self.detect_flag = True
        self.startTask(speed=0.05)

    def ManipulationDetection(self):

        trufor_datect(w_ori=self.src_w_ori, h_ori=self.src_h_ori, w_det=512, h_det=512)

    def GanDetection(self):

        self.clear_layout()
        self.ui_init_image()

        GAN_detector = GAN_Detector()
        self.my_thread = Thread(target=GAN_detector.gan_real_detector, daemon=True)
        self.my_thread.start()
        self.detect_gan_flag = True
        self.startTask(speed=0.02)
        self.textLog.setText("正在进行生成式图像检测,请稍等...")

    def detect_result(self):

        self.clear_layout()
        self.ui_init_image()

        self.dst_image = cv2.imread("result_tmp/mask_detection.png", 0)
        # 置信度
        _, self.dst_image = cv2.threshold(self.dst_image, 255 * max(0.5, self.conf), 255, cv2.THRESH_BINARY)
        cv2.imwrite("result_tmp/dst.png", self.dst_image)

        self.dst_show("result_tmp/dst.png")
        self.textLog.setFont(self.font)
        self.textLog.setText("请滑动滑条查看不同结果图")

        self.slider_1.setRange(0, 11) # 取值范围
        self.slider_label_title.setFont(self.font)
        self.slider_label_title.setText("result_tmp/dst.png")
        # 滑动切换图片
        try:
            self.slider_1.valueChanged.disconnect(self.slider_value_get)
            self.slider_1.valueChanged.connect(self.img_switch)
        except:
            pass

    def inpainting(self):

        self.clear_layout()
        self.ui_init_image()

        src_ori_mask = cv2.imread("result_tmp/mask_ori.png")
        mask = src_ori_mask.copy()

        # 定义膨胀核
        kernel = np.ones((7,7), np.uint8)

        # 膨胀操作
        _, mask = cv2.threshold(mask, 255 * max(0.5, self.conf), 255, cv2.THRESH_BINARY)
        mask = cv2.dilate(mask, kernel, iterations=1)
        cv2.imwrite("result_inpainting/src_mask.png", mask)

        for c in range(mask.shape[2]):
            for i in range(mask.shape[1]):
                for j in range(mask.shape[0]):
                    if mask[j][i][c] == 0:
                        mask[j][i][c] = 1
                    if mask[j][i][c] == 255:
                        mask[j][i][c] = 0

        # 防止爆显存
        mask = cv2.imread("result_inpainting/src_mask.png")
        img = cv2.imread("result_inpainting/src.png")

        if img.shape[0] > 1024 or img.shape[1] > 1024:
            img = cv2.resize(img, (1024, 1024))
            mask = cv2.resize(mask, (1024, 1024))
            cv2.imwrite("result_inpainting/src.png", img)
            cv2.imwrite("result_inpainting/src_mask.png", mask)

        self.my_thread = Thread(target=LaMa_inpainting, daemon=True)
        self.my_thread.start()
        self.inpainting_flag = True
        self.startTask(speed=0.02)

    def inpainting_by_myself(self): 

        self.clear_layout()
        self.ui_init_image()
        
        # 防止爆显存
        image = cv2.imread("result_tmp/src_ori.png")
        cv2.imwrite("result_inpainting/src.png", image)
        image = cv2.imread("result_inpainting/src.png")
        w, h, c = image.shape
        mask = np.zeros([w, h, 1], np.uint8)
        image_copy = image.copy()
        sketch = Sketcher(
            'workspace', [image_copy, mask], lambda: ((255, 255, 255), (255, 255, 255)), painter_args.thick, painter_args.painter)
        self.textLog.setFont(self.font)
        self.textLog.setText("q:quit     r:reset     +:large_thick     -:small_thick     s:start")
        while True:
            ch = cv2.waitKey()
            if ch == ord('q'):
                self.textLog.setText("quit")
                break

            elif ch == ord('r'):
                image_copy[:] = image.copy()
                mask[:] = 0
                sketch.show()
                self.textLog.setText("reset")

            elif ch == ord('+'): 
                sketch.large_thick()
                self.textLog.setText("large_thick")

            elif ch == ord('-'): 
                sketch.small_thick()
                self.textLog.setText("small_thick")

            elif ch == ord('s'):
                mask_tensor = (ToTensor()(mask)).unsqueeze(0)
                masked_tensor = (255 * (mask_tensor).float())
                masked_np = postprocess(masked_tensor[0])

                for i in range(h - 1):
                    for j in range(w - 1):
                        if masked_np[j][i][0] == 255:
                            masked_np[j][i][0] = 1
                        if masked_np[j][i][0] == 127:
                            masked_np[j][i][0] = 0

                cv2.imwrite("./result_inpainting/src_mask.png", masked_np)

                self.my_thread = Thread(target=LaMa_inpainting, daemon=True)
                self.my_thread.start()
                self.inpainting_flag = True
                self.startTask(speed=0.5)
                self.textLog.setText("正在图像修复,请稍等...")

        cv2.destroyAllWindows()

    def super_resolution(self): 

        self.clear_layout()
        self.ui_init_image()    

        scale = ['2', '4']
        value1, ok1 = QInputDialog.getItem(self, 'Input Dialog', '请选择放大倍数:', scale, editable=False)
        self.textLog.setText(f"{self.function[0]}:{self.result_image[0]}\n"
                                f"{self.function[1]}:{self.result_image[1]}\n"
                                f"{self.function[2]}:{self.result_image[2]}\n"
                                f"{self.function[3]}:{self.result_image[3]}\n"
                                f"{self.function[4]}:{self.result_image[4]}\n"
                                f"{self.function[5]}:{self.result_image[5]}\n"
                                f"{self.function[6]}:{self.result_image[6]}\n"
                                f"{self.function[7]}:{self.result_image[7]}\n"
                                f"{self.function[8]}:{self.result_image[8]}\n"
                                f"{self.function[9]}:{self.result_image[9]}\n"
                                f"{self.function[10]}:{self.result_image[10]}\n"
                                f"{self.function[11]}:{self.result_image[11]}\n"
                                )
        if ok1:
            while True:
                try:
                    value2, ok2 = QInputDialog.getItem(self, '放大文件', '请选择放大文件:', self.result_image, editable=False)
                    if ok2 == False:
                        break
                    elif ok2 == True:
                        self.sr_information(value1, value2)
                        self.my_thread = Thread(target=bsrgan_sr.main, kwargs={'sf':self.sr_scale}, daemon=True)
                        self.my_thread.start()
                        self.sr_flag = True
                        self.startTask(speed=0.2)
                        self.textLog.setText("正在进行图像超分辨率,请稍等...")
                        break
                except:
                    self.textLog.setText("请重新选择图片")

    def deblur(self):

        self.clear_layout()
        self.ui_init_image()

        self.my_thread = Thread(target=deblur.main, daemon=True)
        self.my_thread.start()
        self.deblur_flag = True
        self.startTask(speed=1)
        self.textLog.setText("正在进行图像去运动模糊,请稍等...")
        self.textLog.append("该任务耗时较久, 请耐心等待")

    def denoise(self):

        self.clear_layout()
        self.ui_init_image()

        self.my_thread = Thread(target=denoise.main, daemon=True)
        self.my_thread.start()
        self.denoise_flag = True
        self.startTask(speed=0.3)
        self.textLog.setText("正在进行图像去噪,请稍等...")

    def deweather(self):

        self.clear_layout()
        self.ui_init_image()

        # 防止爆显存
        image_tmp = cv2.imread("result_deweather/input/src.png")
        if image_tmp.shape[0] > 512 or image_tmp.shape[1] > 512:
            image_tmp = cv2.resize(image_tmp, (int(image_tmp.shape[1] / 2),int(image_tmp.shape[0] / 2)))
            cv2.imwrite("result_deweather/input/src.png", image_tmp)
            self.textLog.setText(f"图片过大, 已缩放至 {(int(image_tmp.shape[1]),int(image_tmp.shape[0]))}")
        
        self.my_thread = Thread(target=deweather.main, daemon=True)
        self.my_thread.start()
        self.deweather_flag = True
        self.startTask(speed=5)
        self.textLog.append("正在进行图像去雨/雪/雾,请稍等...")
        self.textLog.append("该任务耗时较久, 请耐心等待")

    def startTask(self, speed=None):
        
        # 创建并启动工作线程
        self.worker = WorkerThread(speed=speed)
        self.worker.progress_updated.connect(self.updateProgress)
        self.worker.finished.connect(self.show_finish_message)
        self.worker.start()

    def updateProgress(self, value):
        # 更新进度条
        self.progress_bar.setValue(value)

    def which_sample_clicked(self, sample_num=None):
        
        try:
            self.sample_num = sample_num

            # 记录与读取点击顺序
            try:
                with open(f"logs/sample_num.txt", "r", encoding='utf-8') as f:
                    sample_num_last = int(f.readlines()[-1])
            except:
                sample_num_last = None
            with open(f"logs/sample_num.txt", "a", encoding='utf-8') as f:
                f.write(f"{self.sample_num}\n")

            # 初次缓存
            if sample_num_last == None:
                # sample 缓存至 tmp
                src = f"result_samples/src{self.sample_num}.png"
                dst = "result_tmp/src_ori.png"
                shutil.copyfile(src, dst)
                for i in range(len(self.results_dir)):
                    if self.results_dir[i] == "result_deweather":
                        shutil.copyfile("result_tmp/src_ori.png", os.path.join(self.results_dir[i], "input", "src.png"))
                        shutil.copyfile("result_tmp/src_ori.png", os.path.join(self.results_dir[i], "target", "src.png"))
                    shutil.copyfile("result_tmp/src_ori.png", os.path.join(self.results_dir[i], "src.png"))
        except:
            self.textLog.setText("请先添加图片至检材区")

        # 缓存现在的结果, 保存现场
        for i in range(len(self.results_dir)):
            if self.results_dir[i] == "result_deweather":
                if sample_num_last == None:
                    try:
                        shutil.copyfile(os.path.join("result_deweather/dst.png"), os.path.join(self.results_samples[self.sample_num], "result_deweather/dst.png"))
                    except:
                        pass
                    shutil.copyfile(os.path.join("result_deweather/input/src.png"), os.path.join(self.results_samples[self.sample_num], "result_deweather/input/src.png"))
                    shutil.copyfile(os.path.join("result_deweather/target/src.png"), os.path.join(self.results_samples[self.sample_num], "result_deweather/target/src.png"))
                else:
                    try:
                        shutil.copyfile(os.path.join("result_deweather/dst.png"), os.path.join(self.results_samples[sample_num_last], "result_deweather/dst.png"))
                    except:
                        pass
                    shutil.copyfile(os.path.join("result_deweather/input/src.png"), os.path.join(self.results_samples[sample_num_last], "result_deweather/input/src.png"))
                    shutil.copyfile(os.path.join("result_deweather/target/src.png"), os.path.join(self.results_samples[sample_num_last], "result_deweather/target/src.png"))
            else:
                tmp_dir = os.listdir(self.results_dir[i])
                for j in range(len(tmp_dir)):
                    file = os.listdir(self.results_dir[i])
                    if sample_num_last == None:
                        shutil.copyfile(os.path.join(self.results_dir[i], file[j]), os.path.join(self.results_samples[self.sample_num], self.results_dir[i], file[j]))
                    else:
                        shutil.copyfile(os.path.join(self.results_dir[i], file[j]), os.path.join(self.results_samples[sample_num_last], self.results_dir[i], file[j]))

        # 加载之前的结果, 恢复现场
        self.clear(which='tmp')
        
        dir_src = os.listdir(self.results_samples[self.sample_num])
        for i in range(len(dir_src)):
            if dir_src[i] == "result_deweather":
                shutil.copyfile(os.path.join(self.results_samples[self.sample_num], dir_src[i], "input/src.png"), os.path.join(dir_src[i], "input/src.png"))
                shutil.copyfile(os.path.join(self.results_samples[self.sample_num], dir_src[i], "target/src.png"), os.path.join(dir_src[i], "target/src.png"))
                try:
                    shutil.copyfile(os.path.join(self.results_samples[self.sample_num], dir_src[i], "dst.png"), os.path.join(dir_src[i], "dst.png"))
                except:
                    pass
            else:
                dir_src_tmp = os.listdir(os.path.join(self.results_samples[self.sample_num], dir_src[i]))
                for j in range(len(dir_src_tmp)):    
                    shutil.copyfile(os.path.join(self.results_samples[self.sample_num], dir_src[i], dir_src_tmp[j]), os.path.join(dir_src[i], dir_src_tmp[j]))
        shutil.copyfile("result_tmp/src.png", "result_tmp/src_ori.png")

        # 显示证据图像
        self.my_thread = Thread(target=self.src_show, daemon=True)
        self.my_thread.start()
        self.which_sample_clicked_flag = True
        self.startTask(speed=0.3)
        self.textLog.setText("正在加载证据图像,请稍等...")

    def src_show(self):
        
        self.src_image = cv2.imread("result_tmp/src_ori.png")
        self.src_image = cv2.cvtColor(self.src_image, cv2.COLOR_BGR2RGB)
        self.src_w_ori = self.src_image.shape[1]
        self.src_h_ori = self.src_image.shape[0]
        
        if self.src_w_ori > self.src_h_ori:
                scale = 800 / self.src_w_ori
        else:
                scale = 800 / self.src_h_ori
        self.src_image = cv2.resize(self.src_image, (int(self.src_w_ori*scale), int(self.src_h_ori*scale)), 0, 0, cv2.INTER_LINEAR)

        for j in range(5):
            if j == self.sample_num:
                self.samples[j].setStyleSheet('border:5px solid red;')
            if j != self.sample_num:
                self.samples[j].setStyleSheet('border:2px solid #D7E2F9;')

    def dst_show(self, filenpath):

        # 显示图像
        self.dst_image = cv2.imread(filenpath)
        cv2.imwrite("result_show/dst.png", self.dst_image)
        self.dst_image = cv2.cvtColor(self.dst_image, cv2.COLOR_BGR2RGB)
        # 缩放适应窗口 
        if self.dst_image.shape[0] > self.dst_image.shape[1]:
            scale = 800 / self.dst_image.shape[0]
        else:
            scale = 800 / self.dst_image.shape[1]
        self.dst_image = cv2.resize(self.dst_image, (int(self.dst_image.shape[1]*scale), int(self.dst_image.shape[0]*scale)),\
            0, 0, cv2.INTER_LINEAR)
        
        qImage = QImage(self.dst_image.data, self.dst_image.shape[1], self.dst_image.shape[0], QImage.Format_RGB888)
        self.label_dst_img.setPixmap(QPixmap.fromImage(qImage))
        self.label_dst_path.setText(f"结果图像: {filenpath}")

    def show_finish_message(self):
        
        if self.which_sample_clicked_flag:
            if self.sample_num not in self.samples_num_history:
                self.image_information()
            else:
                self.clear_layout()
                self.ui_init_image()
            self.samples_num_history.append(self.sample_num)
            
            qImage = QImage(self.src_image.data, self.src_image.shape[1], self.src_image.shape[0], QImage.Format_RGB888)
            self.label_src_img.setPixmap(QPixmap.fromImage(qImage))
            self.label_src_path.setText(f"证据图像: {self.images_names[self.sample_num]}")
            
            self.which_sample_clicked_flag = None
        if self.dct_flag:
            self.dst_show("result_plt/DCT.png")
            self.history_show(f"{self.images_names[self.sample_num]} 进行 DCT 直方图生成\n")
            self.textLog.setText("DCT 直方图已生成!")
            self.dct_flag = None
        if self.histogram_flag:
            self.dst_show("result_plt/Color_Histogram.png")
            self.history_show(f"{self.images_names[self.sample_num]} 进行颜色直方图生成\n")
            self.textLog.setText("颜色直方图已生成!")
            self.histogram_flag = None
        if self.detect_flag:
            self.detect_result()
            self.history_show(f"{self.images_names[self.sample_num]} 进行篡改鉴定及定位\n")
            self.textLog.setText("篡改鉴定及定位完成!")
            self.detect_flag = None
        if self.detect_gan_flag:
            file_path = 'logs/gan_detect_score.txt'
            with open(file_path, 'r') as f:
                self.score = float(f.read())
            if self.score < 0.0:
                self.textLog.setText("该图像不是生成式模型生成!")
            else:
                self.textLog.setText("该图像是生成式模型生成!")
            self.history_show(f"{self.images_names[self.sample_num]} 进行生成式图像检测\n")
            self.detect_gan_flag = None
        if self.inpainting_flag:
            self.dst_show("./result_tmp/result_inpainting.jpg")
            self.textLog.setText("图像还原完成!")
            self.history_show(f"{self.images_names[self.sample_num]} 进行图像还原\n")
            self.inpainting_flag = None
        if self.sr_flag:
            self.dst_show("result_sr/dst.png")
            self.textLog.setText("超分辨率完成!")
            self.history_show(f"{self.images_names[self.sample_num]} 进行超分辨率\n")
            self.sr_flag = None
        if self.deblur_flag:
            self.dst_show("./result_deblur/dst.png")
            self.textLog.setText("图像去运动模糊完成!")
            self.history_show(f"{self.images_names[self.sample_num]} 进行图像去运动模糊\n")
            self.deblur_flag = None
        if self.denoise_flag:
            self.dst_show("./result_denoise/dst.png")
            self.textLog.setText("图像去噪完成!")
            self.history_show(f"{self.images_names[self.sample_num]} 进行图像去噪\n")
            self.denoise_flag = None
        if self.deweather_flag:
            self.dst_show("./result_deweather/dst.png")
            self.textLog.setText("去雨/雪/雾完成!")
            self.history_show(f"{self.images_names[self.sample_num]} 进行图像去雨/雪/雾\n")
            self.deweather_flag = None

    def clear_layout(self, which='dst'):
        if which == 'dst':
            # 清除dst布局中的部件
            for i in reversed(range(self.dstLayout.count())):
                widget = self.dstLayout.itemAt(i).widget()
                self.dstLayout.removeWidget(widget)
                widget.setParent(None)
        elif which == 'src':
            # 清除dst布局中的部件
            for i in reversed(range(self.srcLayout.count())):
                widget = self.dstLayout.itemAt(i).widget()
                self.dstLayout.removeWidget(widget)
                widget.setParent(None)

    def img_switch(self, value=0):

        try:
            self.slider_label_title.setFont(self.font)
            self.slider_label_title.setText(self.function[value])
            self.dst_show(self.result_image[value])
            self.textLog.setText("请滑动滑条查看不同结果图")
        except:
            self.label_dst_img.clear()
            self.textLog.setText("当前暂未使用该功能生成图像")

    def sr_information(self, value1=None, value2=None):

        self.sr_scale = int(value1)
        cv2.imwrite("./result_sr/src.png", cv2.imread(value2))
        try:
            os.remove("./result_sr/dst.png")
        except:
            pass
        QMessageBox.information(self, f"放大倍数: {value1}, 超分辨率放大倍数已设置为: {value1}\n", f"放大文件: {value2}")
        self.textLog.setText(f"超分辨率放大倍数已设置为: {value1}\n放大文件: {value2}")

    def history_show(self, message):
        
        with open(f"logs/log_{self.current_time}.txt", "a+", encoding='utf-8') as f:
            f.write(f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}:{message}\n")
            self.historyText.append(f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}:{message}\n")

    def clear(self, which=None):

        if which != None:
            
            # 删除log文件
            if which == "all":
                try:
                    os.remove("logs/sample_num.txt")
                except:
                    pass
                with open("logs/sample_num.txt", 'w', encoding='utf-8') as file:
                    file.write("samples 点击顺序\n")
            # 删除文件夹
            if which == "tmp" or which == "all":
                # 清除缓存文件
                for i in range(len(self.results_dir)):
                    if self.results_dir[i] == "result_samples":
                        continue
                    shutil.rmtree(self.results_dir[i])
                    os.makedirs(self.results_dir[i])
                    if self.results_dir[i] == "result_deweather":
                        os.makedirs("result_deweather/input")
                        os.makedirs("result_deweather/target")
            if which == "samples" or which == "all":
                for i in range(len(self.results_samples)):
                    shutil.rmtree(self.results_samples[i])
                    for j in range(len(self.results_dir)):
                        os.makedirs(os.path.join(self.results_samples[i], self.results_dir[j]))
                        if self.results_dir[j] == "result_deweather":
                            os.makedirs(os.path.join(self.results_samples[i], self.results_dir[j], "input"))
                            os.makedirs(os.path.join(self.results_samples[i], self.results_dir[j], "target"))
            try:
                # 清除 dst_label 显示
                self.label_dst_img.clear()
            except:
                pass

    def quit(self):
        sys.exit()


app = QApplication(sys.argv)
win = my_window()

win.show()
win.showMaximized()
app.exec()