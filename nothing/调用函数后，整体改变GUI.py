import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Layout Example")

        # 创建初始布局
        self.initial_layout = QVBoxLayout()
        self.create_initial_layout()

        # 创建主窗口部件并设置初始布局
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.initial_layout)
        self.setCentralWidget(self.central_widget)

    def create_initial_layout(self):
        # 创建初始布局中的部件
        self.button1 = QPushButton("Option 1")
        self.button2 = QPushButton("Option 2")
        self.button3 = QPushButton("Option 3")

        # 将部件添加到初始布局中
        self.initial_layout.addWidget(self.button1)
        self.initial_layout.addWidget(self.button2)
        self.initial_layout.addWidget(self.button3)

        # 为每个按钮连接相应的槽函数
        self.button1.clicked.connect(self.on_option1_clicked)
        self.button2.clicked.connect(self.on_option2_clicked)
        self.button3.clicked.connect(self.on_option3_clicked)

    def clear_layout(self):
        # 清除初始布局中的部件
        for i in reversed(range(self.initial_layout.count())):
            widget = self.initial_layout.itemAt(i).widget()
            self.initial_layout.removeWidget(widget)
            widget.setParent(None)

    def create_new_layout(self):
        # 创建新的布局
        self.new_layout = QVBoxLayout()
        self.new_layout.addWidget(QPushButton("New Option 1"))
        self.new_layout.addWidget(QPushButton("New Option 2"))
        self.new_layout.addWidget(QPushButton("New Option 3"))

        # 将新布局设置为窗口的布局
        self.central_widget.setLayout(self.new_layout)

    def on_option1_clicked(self):
        self.clear_layout()  # 清除初始布局
        self.create_new_layout()  # 创建新布局

    def on_option2_clicked(self):
        self.clear_layout()  # 清除初始布局
        # 创建并设置其他新布局的方法

    def on_option3_clicked(self):
        self.clear_layout()  # 清除初始布局
        # 创建并设置其他新布局的方法

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
