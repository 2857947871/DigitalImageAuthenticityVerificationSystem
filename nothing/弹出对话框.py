import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QMessageBox

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('String Selection Dialog')
        self.setGeometry(100, 100, 300, 200)

        button = QPushButton('Select Fruit', self)
        button.clicked.connect(self.select_fruit)

    def select_fruit(self):
        # 定义可选的水果列表
        fruits = ['Apple', 'Orange', 'Banana', 'Grape', 'Peach']

        # 显示包含可选项的对话框
        fruit, ok = QInputDialog.getItem(self, 'Select Fruit', 'Choose a fruit:', fruits, editable=False)

        if ok and fruit:
            self.display_selection(fruit)

    def display_selection(self, fruit):
        QMessageBox.information(self, 'Selection', f'You selected: {fruit}')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    sys.exit(app.exec_())