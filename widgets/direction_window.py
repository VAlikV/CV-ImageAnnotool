from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
# from widgets.sam2 import SAM2
import os
import cv2
import numpy as np

class DirectionWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.current_file_index = -1
        self.file_list = []

        # self.colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255))
        self.color = [0,0,255]
        # np.random.uniform(0, 256, 3)

        self.zoom = 1
        self.min_zoom = 1
        self.max_zoom = 10
        self.x_offset, self.y_offset = 0, 0

        self.points = np.array([[0,0],[0,0]])
        self.stage = 0

        self.image_height, self.image_width = 224, 224
        self.new_height, self.new_width = self.image_height, self.image_width

        # =======================================================
        
        self.setWindowTitle("Dataset Prepare by 431Group")

        # =======================================================

        self.prev_button = QPushButton("Prev")
        self.next_button = QPushButton("Next")
        self.file_name_line = QLineEdit()
        self.file_name_line.setReadOnly(True)
        self.up_layout = QHBoxLayout()
        self.up_layout.addWidget(self.prev_button)
        self.up_layout.addWidget(self.file_name_line)
        self.up_layout.addWidget(self.next_button)

        # =======================================================

        self.cancel_button = QPushButton("Cancel")
        self.generate_button = QPushButton("Generate")
        self.down_layout = QHBoxLayout()
        self.down_layout.addWidget(self.cancel_button)
        self.down_layout.addWidget(self.generate_button)

        # =======================================================

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.up_layout)
        self.main_layout.addLayout(self.down_layout)     

        self.setLayout(self.main_layout)

        # =======================================================

        self.setConnectoins()

        # =======================================================

        self.updateFileList()
        # self.file_name = self.file_list[0]
        # self.file_name_line.setText(self.file_name)
    
# -------------------------------------------------------------------------

    def setConnectoins(self):
        self.next_button.clicked.connect(self.selectNextFile)
        self.prev_button.clicked.connect(self.selectPrevFile)

        self.cancel_button.clicked.connect(self.cancel)
        self.generate_button.clicked.connect(self.generateLable)

# -------------------------------------------------------------------------
# Обновление списка файлов 
# -------------------------------------------------------------------------

    def updateFileList(self):
        self.file_list = os.listdir("input")

# -------------------------------------------------------------------------
# Выбор следующего файла
# -------------------------------------------------------------------------

    def selectNextFile(self):
        if self.current_file_index < len(self.file_list) - 1:
            self.current_file_index += 1
            self.file_name = self.file_list[self.current_file_index]
            self.file_name_line.setText(self.file_name)
        else:
            self.current_file_index = 0
            self.file_name = self.file_list[self.current_file_index]
            self.file_name_line.setText(self.file_name)
        self.zoom = 1
        self.x_offset, self.y_offset = 0, 0
        self.openFile()

# -------------------------------------------------------------------------
# Выбор предыдущего файла
# -------------------------------------------------------------------------

    def selectPrevFile(self):
        if self.current_file_index > 0:
            self.current_file_index -= 1
            self.file_name = self.file_list[self.current_file_index]
            self.file_name_line.setText(self.file_name)
        else:
            self.current_file_index = len(self.file_list) - 1
            self.file_name = self.file_list[self.current_file_index]
            self.file_name_line.setText(self.file_name)
        self.zoom = 1
        self.x_offset, self.y_offset = 0, 0
        self.openFile()

# -------------------------------------------------------------------------
# Открытие изображения из папки input
# -------------------------------------------------------------------------

    def openFile(self):
        if self.file_name[len(self.file_name)-3:len(self.file_name)] == "jpg" or self.file_name[len(self.file_name)-3:len(self.file_name)] == "png":
            self.stage = 0

            self.image = cv2.imread("input/" + self.file_name)
            self.image = cv2.resize(self.image, (self.image_width, self.image_height))

            self.raw_image = self.image.copy()
            cv2.namedWindow("Image")
            cv2.setMouseCallback("Image", self.callback)
            cv2.imshow("Image", self.image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

# -------------------------------------------------------------------------
# Обработка колесика мыши и нажатия левой кнопки мыши 
# -------------------------------------------------------------------------

    def callback(self, event, x, y, flags, param):

        x = round(x / self.zoom) + self.x_offset
        y = round(y / self.zoom) + self.y_offset

        if event == cv2.EVENT_LBUTTONDOWN:
            # print("x: ", x, "y: ", y)
            self.takePoint(x, y)
        
        if event == cv2.EVENT_RBUTTONDOWN:
            # print("x: ", x, "y: ", y)
            self.takePoint(x, y)

        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.zoom *= 1.1
                self.zoom = min(self.zoom, self.max_zoom)
            else:
                self.zoom /= 1.1
                self.zoom = max(self.zoom, self.min_zoom)

            # Calculate zoomed-in image size
            self.new_width = round(self.image.shape[1] / self.zoom)
            self.new_height = round(self.image.shape[0] / self.zoom)

            # Calculate offset
            self.x_offset = round(x - (x / self.zoom))
            self.y_offset = round(y - (y / self.zoom))

            self.printImage()

# -------------------------------------------------------------------------
# Отрисовка окна  
# -------------------------------------------------------------------------

    def printImage(self):
        img = self.image.copy()

        # Crop image
        img = img[
            self.y_offset : self.y_offset + self.new_height,
            self.x_offset : self.x_offset + self.new_width,
        ]

        # Stretch image to full size
        img = cv2.resize(img, (self.image.shape[1], self.image.shape[0]))
        cv2.imshow("Image", img)

# -------------------------------------------------------------------------
# Запись координат вектора  
# -------------------------------------------------------------------------

    def takePoint(self, x, y):
        if self.stage == 0:
            self.points[0,0] = x
            self.points[0,1] = y
            self.stage = 1
        elif self.stage >= 1:
            self.points[1,0] = x - self.points[0,0]
            self.points[1,1] = y - self.points[0,1]
            self.stage = 2

        # print(self.points)
        self.printVector()

# -------------------------------------------------------------------------
# Отрисовка 
# -------------------------------------------------------------------------

    def printVector(self):
        self.image = self.raw_image.copy()
        if self.stage == 1:
            self.image = cv2.circle(self.image, self.points[0,:], 3, self.color, 3)
        elif self.stage == 2:
            self.image = cv2.circle(self.image, self.points[0,:], 3, self.color, 3)
            self.image = cv2.line(self.image, self.points[0,:], self.points[0,:]+self.points[1,:], self.color, 2)

        self.printImage()

# -------------------------------------------------------------------------
# Отмена
# -------------------------------------------------------------------------

    def cancel(self):
        self.points[:,:] = 0
        self.image = self.raw_image.copy()
        self.printImage()
        self.stage = 0
        print("Cancel")

# -------------------------------------------------------------------------
# Генерация лейбла
# -------------------------------------------------------------------------

    def generateLable(self):
        if self.stage == 2:
            with open("output/" + self.file_name[0:-4] + ".txt", "w") as f:
                x = self.points[0,0]/self.image_height
                y = self.points[0,1]/self.image_width
                dx = self.points[1,0]/np.sqrt(self.points[1,0]**2 + self.points[1,1]**2)
                dy = self.points[1,1]/np.sqrt(self.points[1,0]**2 + self.points[1,1]**2)

                line = str(x) 
                line += " " + str(y)
                line += " " + str(dx)
                line += " " + str(dy)
                f.write(line)
        print(self.file_name[0:-4] + " Coplete!")
        print("===")
