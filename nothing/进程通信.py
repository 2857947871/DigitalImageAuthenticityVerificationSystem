import sys
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication, QMainWindow, QTextEdit, QVBoxLayout, QWidget, QPushButton

class Worker(QThread):
    text_signal = pyqtSignal(str)

    def run(self):
        """模拟一个后台任务"""
        # 模拟一些处理
        self.sleep(2)
        self.text_signal.emit("任务完成，更新文本光标")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.text_edit = QTextEdit(self)
        self.text_edit.setText("这是一个文本编辑器")

        self.button = QPushButton("开始任务", self)
        self.button.clicked.connect(self.start_task)

        layout = QVBoxLayout()
        layout.addWidget(self.text_edit)
        layout.addWidget(self.button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def start_task(self):
        self.worker = Worker()
        self.worker.text_signal.connect(self.update_text_edit)
        self.worker.start()

    @pyqtSlot(str)
    def update_text_edit(self, text):
        self.text_edit.append(text)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
