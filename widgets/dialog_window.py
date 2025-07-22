
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QDialog

class DialogWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select mode")

        self.selected_option = None  # параметр, который пользователь выберет

        self.combo = QComboBox()
        self.combo.addItems(["Segmentation", "Direction"])

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Mode:"))
        layout.addWidget(self.combo)
        layout.addWidget(self.ok_button)
        self.setLayout(layout)

    def accept(self):
        self.selected_option = self.combo.currentIndex()
        super().accept()  # Закрывает диалог с кодом Accepted