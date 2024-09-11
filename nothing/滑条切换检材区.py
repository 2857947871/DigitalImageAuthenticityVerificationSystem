import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QSlider, QHBoxLayout
from PyQt5.QtCore import Qt

class SliderLabelApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Vertical Slider to Switch Labels')
        self.setGeometry(100, 100, 400, 300)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 创建主布局
        self.main_layout = QHBoxLayout()  # 使用水平布局器将滑条和标签布局器放在一行

        # 创建标签列表
        self.labels_layout = QVBoxLayout()  # 垂直布局器
        self.labels = [QLabel(f'Label {i}') for i in range(1, 14)]
        for label in self.labels:
            label.setAlignment(Qt.AlignCenter)  # 居中对齐
            label.setStyleSheet('border: 1px solid black; padding: 10px;')  # 设置样式
            label.setVisible(False)  # 初始时隐藏所有标签
            self.labels_layout.addWidget(label)

        # 显示第一个标签
        self.labels[0].setVisible(True)

        # 创建滑条
        self.slider = QSlider(Qt.Vertical)
        self.slider.setMinimum(1)
        self.slider.setMaximum(len(self.labels) - 1)
        self.slider.setValue(1)
        self.slider.valueChanged.connect(self.change_label)

        # 将滑条和标签布局器添加到主布局中
        self.main_layout.addLayout(self.labels_layout)
        self.main_layout.addWidget(self.slider)

        self.central_widget.setLayout(self.main_layout)

    def change_label(self, value):
        
        # 隐藏所有标签
        for label in self.labels:
            label.setVisible(False)
        # 仅显示当前滑条值对应的标签
        self.labels[value].setVisible(True)
        self.labels[value - 1].setVisible(True)
        self.labels[value - 2].setVisible(True)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SliderLabelApp()
    window.show()
    sys.exit(app.exec_())
