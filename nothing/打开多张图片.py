import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QFileDialog, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Multi Image Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.labels = []

        self.open_images()

    def open_images(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Open Images", "", "Images (*.png *.xpm *.jpg *.bmp *.gif)", options=options)
        if files:
            for file in files:
                label = QLabel(self)
                pixmap = QPixmap(file)
                label.setPixmap(pixmap.scaledToWidth(400))
                self.layout.addWidget(label)
                self.labels.append(label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = ImageViewer()
    viewer.show()
    sys.exit(app.exec_())
