from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QVBoxLayout, QWidget, QLabel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 创建一个按钮
        button = QPushButton()
        button.setStyleSheet("border:none;")  # 移除按钮的边框样式

        # 创建一个布局，并将按钮添加到布局中
        layout = QVBoxLayout()
        layout.addWidget(button)

        # 创建一个 QLabel，并设置文本
        label = QLabel("Click me!")
        label.setAlignment(Qt.AlignCenter)  # 文本居中显示

        # 将 QLabel 放置在按钮上
        button.setLayout(layout)
        button.setFixedSize(label.sizeHint())  # 设置按钮的大小与 QLabel 相同
        button.clicked.connect(self.label_clicked)  # 连接按钮的点击信号到相应的函数

        self.setCentralWidget(button)

    def label_clicked(self):
        print("Label clicked!")

if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec_()
