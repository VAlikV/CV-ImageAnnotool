from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QListWidget
from PyQt5 import QtCore
# from widgets.sam2 import SAM2
import os
import cv2
import numpy as np
from ultralytics import YOLO

class DetectionWindow(QWidget):
    def __init__(self, image_height = 900, image_width = 1600):
        super().__init__()

        self.classes = ["Connector", "Capacitor", "Led", "Relay", "Coil"]
        self.current_class = self.classes[0]
        self.current_object_name = self.classes[0] + "_0"
        self.current_file_index = -1
        self.file_list = []

        colors = [(0, 0, 255), (255, 0, 0), (0, 255, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255)]
        # self.colors = np.random.uniform(0, 256, (len(self.classes),3))

        self.classes_color = {}
        for i, c in enumerate(self.classes):
            self.classes_color[c] = colors[i]
        
        self.color = self.classes_color[self.current_class]

        self.objects_count = {}
        for c in self.classes:
            self.objects_count[c] = 0

        self.objects = {}
        self.current_object = {}

        self.zoom = 1
        self.min_zoom = 1
        self.max_zoom = 10
        self.x_offset, self.y_offset = 0, 0

        if image_height >= 1000:
            self.mult = 2
        else:
            self.mult = 1

        self.source_height, self.source_width = image_height, image_width                       # Нужный размер
        self.image_height, self.image_width = image_height//self.mult, image_width//self.mult   # Уменьшенный размер
        self.new_height, self.new_width = image_height//self.mult, image_width//self.mult       # Уменьшенный размер + зум

        # self.model = SAM2()
        self.points = np.array([[0,0],[0,0]])
        self.stage = 0

        # =======================================================
        
        self.setLayoutSetup()
        self.setConnectoins()
        self.updateFileList()
    
# -------------------------------------------------------------------------
# Настройка окна
# -------------------------------------------------------------------------

    def setLayoutSetup(self):
        self.setWindowTitle("Dataset Prepare by 431Group")

        # =======================================================

        self.prev_button = QPushButton("Prev (q)")
        self.next_button = QPushButton("Next (e)")
        self.file_name_line = QLineEdit()
        self.file_name_line.setReadOnly(True)
        self.up_layout = QHBoxLayout()
        self.up_layout.addWidget(self.prev_button)
        self.up_layout.addWidget(self.file_name_line)
        self.up_layout.addWidget(self.next_button)

        # =======================================================

        self.open_button = QPushButton("Open (a)")
        self.auto_button = QPushButton("Auto")
        self.open_layout = QHBoxLayout()
        self.open_layout.addStretch(1)
        self.open_layout.addWidget(self.open_button)
        self.open_layout.addWidget(self.auto_button)
        self.open_layout.addStretch(1)

        # =======================================================

        self.combobox_classes = QComboBox()
        self.combobox_classes.setFixedWidth(120)
        self.combobox_classes.addItems(self.classes)
        self.middle_layout = QHBoxLayout()
        self.middle_layout.addWidget(QLabel("Class: "))
        self.middle_layout.addWidget(self.combobox_classes)
        self.middle_layout.addStretch(1)    

        # =======================================================

        self.delete_button = QPushButton("Delete")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("Ok (w)")
        self.generate_button = QPushButton("Generate (d)")
        self.down_layout = QHBoxLayout()
        self.down_layout.addWidget(self.delete_button)
        self.delete_button.setEnabled(False)
        self.down_layout.addWidget(self.cancel_button)
        self.down_layout.addWidget(self.ok_button)
        self.down_layout.addWidget(self.generate_button)

        # =======================================================

        self.left_layout = QVBoxLayout()
        self.left_layout.addLayout(self.up_layout)
        self.left_layout.addLayout(self.open_layout)
        self.left_layout.addLayout(self.middle_layout)
        self.left_layout.addLayout(self.down_layout)   

        # =======================================================

        self.right_layout = QVBoxLayout() 
        self.objects_list = QListWidget()
        self.right_layout.addWidget(self.objects_list)

        # =======================================================

        self.main_layout = QHBoxLayout()
        self.main_layout.addLayout(self.left_layout)
        self.main_layout.addLayout(self.right_layout)

        self.setLayout(self.main_layout)

        # =======================================================

# -------------------------------------------------------------------------
# Подключение сигналов
# -------------------------------------------------------------------------

    def setConnectoins(self):
        self.next_button.clicked.connect(self.selectNextFile)
        self.prev_button.clicked.connect(self.selectPrevFile)

        self.combobox_classes.currentIndexChanged.connect(self.selectNewClass)
        self.ok_button.clicked.connect(self.completeObject)
        self.cancel_button.clicked.connect(self.cancelObject)
        self.generate_button.clicked.connect(self.generateLable)
        self.delete_button.clicked.connect(self.deleteObject)

        self.objects_list.currentItemChanged.connect(self.selectObject)

        self.open_button.clicked.connect(self.openLabel)

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
        
        self.openFile()

# -------------------------------------------------------------------------
# Открытие изображения из папки input
# -------------------------------------------------------------------------

    def openFile(self):
        self.zoom = 1
        self.x_offset, self.y_offset = 0, 0

        if self.file_name[len(self.file_name)-3:len(self.file_name)] == "jpg" or self.file_name[len(self.file_name)-3:len(self.file_name)] == "png":
            
            self.objects_list.clear()

            self.objects_count = {}
            for c in self.classes:
                self.objects_count[c] = 0

            self.objects = {}
            self.current_object = {}

            self.points = np.array([[0,0],[0,0]])

            self.current_object_name = self.current_class + "_" + str(self.objects_count[self.current_class])

            self.source_image = cv2.imread("input/" + self.file_name)
            self.source_image = cv2.resize(self.source_image, (self.source_width, self.source_height))
            
            self.resized_image = cv2.resize(self.source_image, (self.image_width, self.image_height))
            self.masked_image = self.resized_image.copy()

            cv2.namedWindow("Image")
            cv2.setMouseCallback("Image", self.callback)
            cv2.imshow("Image", self.masked_image)
            cv2.waitKey(0)

            # if key == ord('a'):
            #     self.openLabel()
            # elif key == ord('w'):
            #     self.completeObject()
            # elif key == ord('d'):
            #     self.generateLable()
            # elif key == ord('e'):
            #     self.selectNextFile()
            # elif key == ord('q'):
            #     self.selectPrevFile()
            # # cv2.destroyAllWindows()

# -------------------------------------------------------------------------
# Выбор нового класса  
# -------------------------------------------------------------------------

    def selectNewClass(self):
        if not (self.combobox_classes.currentText() == self.current_class):
            # self.completeObject()
            self.current_class = self.combobox_classes.currentText()
            self.current_object_name = self.current_class + "_" + str(self.objects_count[self.current_class])
            self.color = self.classes_color[self.current_class]
            print("Selected: ", self.current_object_name)

# -------------------------------------------------------------------------
# Обработка колесика мыши и нажатия левой кнопки мыши 
# -------------------------------------------------------------------------

    def callback(self, event, x, y, flags, param):

        x = round(x / self.zoom) + self.x_offset
        y = round(y / self.zoom) + self.y_offset

        if event == cv2.EVENT_LBUTTONDOWN:
            # print("x: ", x, "y: ", y)
            self.left_flag = True
            self.takePoint(x*self.mult, y*self.mult)

        if event == cv2.EVENT_LBUTTONUP:
            self.left_flag = False

        # if (self.left_flag) and (event == cv2.EVENT_MOUSEMOVE):
        #     if self.draw_count >= 5:
        #         self.draw_count = 0
        #     self.draw_count += 1

        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.zoom *= 1.1
                self.zoom = min(self.zoom, self.max_zoom)
            else:
                self.zoom /= 1.1
                self.zoom = max(self.zoom, self.min_zoom)

            # Calculate zoomed-in image size
            self.new_width = round(self.masked_image.shape[1] / self.zoom)
            self.new_height = round(self.masked_image.shape[0] / self.zoom)

            # Calculate offset
            self.x_offset = round(x - (x / self.zoom))
            self.y_offset = round(y - (y / self.zoom))

            self.printImage()

# -------------------------------------------------------------------------
# Отрисовка окна  
# -------------------------------------------------------------------------

    def printImage(self):
        img = self.masked_image.copy()

        # Crop image
        img = img[
            self.y_offset : self.y_offset + self.new_height,
            self.x_offset : self.x_offset + self.new_width,
        ]

        # Stretch image to full size
        img = cv2.resize(img, (self.masked_image.shape[1], self.masked_image.shape[0]))
        cv2.imshow("Image", img)

# -------------------------------------------------------------------------
# Прямой проход по sam  
# -------------------------------------------------------------------------

    def takePoint(self, x, y):
        if self.stage == 0:
            self.points[0,0] = x
            self.points[0,1] = y
            self.stage = 1
        elif self.stage >= 1:
            self.points[1,0] = x
            self.points[1,1] = y
            self.stage = 2
            self.current_object["box"] = self.points

        # print(self.points)
        self.printBox()

# -------------------------------------------------------------------------
# Отрисовка маски 
# -------------------------------------------------------------------------

    def printBox(self):
        self.masked_image = self.resized_image.copy()

        if len(self.current_object.keys()) > 0:
            box = self.current_object["box"]
            self.color = self.classes_color[self.current_class]
            self.masked_image = cv2.rectangle(self.masked_image, box[0]//self.mult, box[1]//self.mult, self.color, 2)

        for obj in self.objects.keys():
            box = self.objects[obj]["box"]
            color = self.classes_color[obj[0:obj.find("_")]]
            self.masked_image = cv2.rectangle(self.masked_image, box[0]//self.mult, box[1]//self.mult, color, 1)

        img = self.masked_image.copy()
        img = img[
            self.y_offset : self.y_offset + self.new_height,
            self.x_offset : self.x_offset + self.new_width,
        ]

        img = cv2.resize(img, (self.masked_image.shape[1], self.masked_image.shape[0]))

        cv2.imshow("Image", img)

# -------------------------------------------------------------------------
# Завершение сегентации объекта 
# -------------------------------------------------------------------------

    def completeObject(self):
        if self.current_object_name not in self.objects.keys():
            self.objects_count[self.current_class] += 1

        if len(self.current_object.keys()) > 0:
            self.objects[self.current_object_name] = {}
            self.objects[self.current_object_name]["box"] = self.current_object["box"]

            self.points = np.array([[0,0],[0,0]])
            self.stage = 0
            self.current_object = {}

            print("Add ", self.current_object_name)

            items = [self.objects_list.item(x).text() for x in range(self.objects_list.count())]
            if self.current_object_name not in items:
                self.objects_list.addItem(self.current_object_name)

            self.current_object_name = self.current_class + "_" + str(self.objects_count[self.current_class])
            self.combobox_classes.setEnabled(True)
            self.delete_button.setEnabled(False)

# -------------------------------------------------------------------------
# Отмена сегентации объекта 
# -------------------------------------------------------------------------

    def cancelObject(self):
        self.current_object = {}
        self.points = np.array([[0,0],[0,0]])
        self.stage = 0
        print("Cancel")

        self.combobox_classes.setEnabled(True)
        self.delete_button.setEnabled(False)

        self.current_object_name = self.current_class + "_" + str(self.objects_count[self.current_class])

        self.printBox()

# -------------------------------------------------------------------------
# выбор объекта 
# -------------------------------------------------------------------------

    def selectObject(self):

        if not (self.objects_list.currentItem() is None):

            self.current_object_name = self.objects_list.currentItem().text()
            self.current_object = self.objects[self.current_object_name]
            self.current_class = self.current_object_name[0:self.current_object_name.find("_")]

            self.points = np.array([[0,0],[0,0]])
            self.color = self.classes_color[self.current_class]
            print("Select object: ", self.current_object_name)
            self.combobox_classes.setEnabled(False)
            self.delete_button.setEnabled(True)

            self.printBox()

# -------------------------------------------------------------------------
# Удаление объекта
# -------------------------------------------------------------------------

    def deleteObject(self):

        if self.current_object_name in self.objects.keys():

            self.objects.pop(self.current_object_name)

            self.points = np.array([[0,0],[0,0]])
            self.stage = 0
            self.current_object = {}

            print("Delete ", self.current_object_name)

            items = [self.objects_list.item(x).text() for x in range(self.objects_list.count())]
            if self.current_object_name in items:
                self.objects_list.takeItem(items.index(self.current_object_name))

            self.combobox_classes.setEnabled(True)
            self.delete_button.setEnabled(False)

            self.printBox()
            self.cancelObject()

# -------------------------------------------------------------------------
# Формирование контура
# -------------------------------------------------------------------------

    def create_yolo_line_from_bbox(self, class_id, x1, y1, x2, y2, image_width, image_height):
        """
        Преобразует bbox из формата (x1, y1, x2, y2) в YOLO-формат строки:
        'class_id x_center y_center width height' (все нормировано в 0..1).
        Делает базовую санити-проверку и клиппинг.
        """
        # Преобразуем к float и упорядочим углы
        x1, y1, x2, y2 = map(float, (x1, y1, x2, y2))
        if x2 < x1:
            x1, x2 = x2, x1
        if y2 < y1:
            y1, y2 = y2, y1

        # Клиппим в пределы изображения
        x1 = max(0.0, min(x1, image_width  - 1.0))
        x2 = max(0.0, min(x2, image_width  - 1.0))
        y1 = max(0.0, min(y1, image_height - 1.0))
        y2 = max(0.0, min(y2, image_height - 1.0))

        # Размеры бокса
        bw = x2 - x1
        bh = y2 - y1
        if bw <= 0 or bh <= 0:
            return None  # некорректный бокс — пропускаем

        # Центр и нормализация
        x_center = (x1 + x2) / 2.0 / image_width
        y_center = (y1 + y2) / 2.0 / image_height
        width    = bw / image_width
        height   = bh / image_height

        # Доп. проверка на выход за [0,1] из-за округления/клиппинга
        if not (0.0 <= x_center <= 1.0 and 0.0 <= y_center <= 1.0 and
                0.0 <  width   <= 1.0 and 0.0 <  height  <= 1.0):
            return None

        return f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
    
# -------------------------------------------------------------------------
# Генерация лейбла
# -------------------------------------------------------------------------

    def generateLable(self):
        """
        Генерация .txt с YOLO-боксами: одна строка на объект.
        Используется логика сопоставления класса: если имя класса self.classes[i] входит в ключ объекта.
        Предполагается, что размер исходного изображения: self.source_width, self.source_height.
        """
        out_path = f"output/{self.file_name[:-4]}.txt"
        lines = []

        for key, obj in self.objects.items():
            # Находим id класса по подстроке в ключе (как у вас в сегментации)
            class_id = None
            for i, cname in enumerate(self.classes):
                if cname in key:
                    class_id = i
                    break

            x1, y1 = obj['box'][0]
            x2, y2 = obj['box'][1]

            line = self.create_yolo_line_from_bbox(
                class_id,
                x1, y1, x2, y2,
                self.source_width, self.source_height
            )
            lines.append(line)

        # Записываем файл (перезапишет, как и у вас)
        with open(out_path, "w") as f:
            for ln in lines:
                f.write(ln + "\n")

        print(self.file_name[0:-4] + " Detection labels complete!")
        
# -------------------------------------------------------------------------
# Загрузка лейбла
# -------------------------------------------------------------------------

    def openLabel(self):
        with open("output/" + self.file_name[0:-4] + ".txt", "r") as f:
            self.zoom = 1
            self.x_offset, self.y_offset = 0, 0

            self.objects_count = {}
            for c in self.classes:
                self.objects_count[c] = 0

            self.objects = {}
            self.current_object = {}

            self.points = np.array([[0,0],[0,0]])

            self.objects_list.clear()

            lines = f.readlines()

            h, w = self.source_image.shape[:2]

            # Перебираем все аннотированные объекты
            for line in lines:
                parts = line.strip().split()
                cls_id = int(parts[0])
                coords = list(map(float, parts[1:]))
                xc = float(coords[0]) * w
                yc = float(coords[1]) * h
                width = float(coords[2]) * w
                height = float(coords[3]) * h

                points = np.array([[int(xc-width/2), int(yc-height/2)],[int(xc+width/2), int(yc+height/2)]])
                
                name = self.classes[cls_id]+"_"+str(self.objects_count[self.classes[cls_id]])
                self.objects[name] = {}
                self.objects[name]["box"] = points
                self.objects_count[self.classes[cls_id]] += 1

                self.objects_list.addItem(name)

            self.current_object_name = self.current_class + "_" + str(self.objects_count[self.current_class])
            self.printBox()