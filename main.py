import sys
from PyQt5.QtWidgets import QApplication, QDialog
from widgets.segmentation_window import SegmentWindow
from widgets.dialog_window import DialogWindow
from widgets.direction_window import DirectionWindow
 
if __name__ == "__main__":
    app = QApplication(sys.argv)

    dialog = DialogWindow()
    if dialog.exec_() == QDialog.Accepted:
        selected = dialog.selected_option
        if selected == 0:
            window = SegmentWindow()
        elif selected == 1:
            window = DirectionWindow()
        window.show()
        window.setFixedSize(300,150)
        sys.exit(app.exec_())  # запускаем только если диалог был успешно завершён
    else:
        print("Пользователь закрыл диалог")
        sys.exit(0)

    