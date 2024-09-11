import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QComboBox, QVBoxLayout, QWidget

class DropdownExample(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dropdown Menu Example")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        # 创建标签
        self.label = QLabel("Selected: ", self)
        layout.addWidget(self.label)

        # 创建下拉菜单
        self.dropdown = QComboBox(self)
        self.dropdown.addItems(["Option 1", "Option 2", "Option 3"])
        self.dropdown.activated[str].connect(self.on_select)
        layout.addWidget(self.dropdown)

        # 创建主widget并设置布局
        main_widget = QWidget(self)
        main_widget.setLayout(layout)
        self.setCentralWidget(main_widget)

    def on_select(self, selected_item):
        self.label.setText(f"Selected: {selected_item}")

        if selected_item == "Option 1":
            self.function_for_option_1()
        elif selected_item == "Option 2":
            self.function_for_option_2()
        elif selected_item == "Option 3":
            self.function_for_option_3()

    def function_for_option_1(self):
        print("Performing action for Option 1")

    def function_for_option_2(self):
        print("Performing action for Option 2")

    def function_for_option_3(self):
        print("Performing action for Option 3")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DropdownExample()
    window.show()
    sys.exit(app.exec_())
