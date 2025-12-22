import sys
from PyQt5.QtWidgets import QApplication, QDialog
from widgets.segmentation_window import SegmentWindow
from widgets.dialog_window import DialogWindow
from widgets.direction_window import DirectionWindow
from widgets.detection_window import DetectionWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = DialogWindow()
    if dialog.exec_() == QDialog.Accepted:
        selected = dialog.selected_option
        if selected == 0:
            window = SegmentWindow(image_height = 928, image_width = 1600, classes=["Connector", "Capacitor", "Led", "Relay", "Coil", "Varistor", "Blue-connector", "Terminal"])
        elif selected == 1:
            window = DetectionWindow(image_height = 180, image_width = 320, classes=["PCB"])
        elif selected == 2:
            window = DirectionWindow()
        window.show()
        window.setFixedSize(450,200)
        sys.exit(app.exec_())  # запускаем только если диалог был успешно завершён
    else:
        print("Пользователь закрыл диалог")
        sys.exit(0)

    
    