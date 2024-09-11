import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

class ImageSliderApp(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Image Slider')
        self.setGeometry(100, 100, 400, 300)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.slider = QSlider(Qt.Horizontal, self)
        self.slider.setMinimum(1)
        self.slider.setMaximum(3)
        self.slider.setValue(1)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setTickInterval(1)

        layout = QVBoxLayout()
        layout.addWidget(self.image_label)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.slider.valueChanged.connect(self.updateImage)

        self.updateImage(1)  # 初始显示第一张图片

    def updateImage(self, value):
        image_path = f'images/image_{value}.jpg'  # 假设图片名称为image_1.jpg, image_2.jpg, image_3.jpg
        pixmap = QPixmap(image_path)
        self.image_label.setPixmap(pixmap.scaledToWidth(300))  # 根据标签宽度缩放图片

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ImageSliderApp()
    window.show()
    sys.exit(app.exec_())
