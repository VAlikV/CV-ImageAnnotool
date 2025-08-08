from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox, QCheckBox, QListWidget
from PyQt5 import QtCore
from widgets.sam2 import SAM2
import os
import cv2
import numpy as np

class SegmentWindow(QWidget):
    def __init__(self, image_height = 900, image_width = 1600):
        super().__init__()

        self.classes = ["Connector", "Capacitor", "Led"]
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

        self.source_height, self.source_width = image_height, image_width       # Нужный размер
        self.image_height, self.image_width = image_height//self.mult, image_width//self.mult   # Уменьшенный размер
        self.new_height, self.new_width = image_height//self.mult, image_width//self.mult       # Уменьшенный размер + зум

        self.model = SAM2()
        self.points = []
        self.labels = []

        self.draw = False
        self.left_flag = False
        self.right_flag = False
        self.draw_count = 0
        self.draw_size = 5

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

        self.prev_button = QPushButton("Prev")
        self.next_button = QPushButton("Next")
        self.file_name_line = QLineEdit()
        self.file_name_line.setReadOnly(True)
        self.up_layout = QHBoxLayout()
        self.up_layout.addWidget(self.prev_button)
        self.up_layout.addWidget(self.file_name_line)
        self.up_layout.addWidget(self.next_button)

        # =======================================================

        self.open_button = QPushButton("Open")
        self.open_layout = QHBoxLayout()
        self.open_layout.addStretch(1)
        self.open_layout.addWidget(self.open_button)
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

        self.draw_check_box = QCheckBox()
        self.draw_size_edit = QLineEdit()
        self.draw_size_edit.setText("5")
        self.draw_size_edit.setFixedWidth(25)
        self.draw_size_edit.setInputMask("99")
        self.draw_layout = QHBoxLayout()
        self.draw_layout.addWidget(QLabel("Draw: "))
        self.draw_layout.addWidget(self.draw_check_box)
        self.draw_layout.addWidget(QLabel("Size: "))
        self.draw_layout.addWidget(self.draw_size_edit)
        self.draw_layout.addStretch(1)

        # =======================================================

        self.delete_button = QPushButton("Delete")
        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("Ok")
        self.generate_button = QPushButton("Generate")
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
        self.left_layout.addLayout(self.draw_layout)
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

        self.draw_size_edit.textChanged.connect(self.setDrawSize)

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

            self.points = []
            self.labels = []

            self.current_object_name = self.current_class + "_" + str(self.objects_count[self.current_class])

            self.source_image = cv2.imread("input/" + self.file_name)
            self.source_image = cv2.resize(self.source_image, (self.source_width, self.source_height))
            
            self.resized_image = cv2.resize(self.source_image, (self.image_width, self.image_height))
            self.masked_image = self.resized_image.copy()

            cv2.namedWindow("Image")
            cv2.setMouseCallback("Image", self.callback)
            cv2.imshow("Image", self.masked_image)
            key = cv2.waitKey(0)

            if key == ord('a'):
                self.openLabel()
            elif key == ord('w'):
                self.completeObject()
            elif key == ord('d'):
                self.generateLable()
            elif key == ord('e'):
                self.selectNextFile()
            elif key == ord('q'):
                self.selectPrevFile()
            # cv2.destroyAllWindows()

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

    def setDrawSize(self):
        self.draw_size = int(self.draw_size_edit.text())

# -------------------------------------------------------------------------
# Обработка колесика мыши и нажатия левой кнопки мыши 
# -------------------------------------------------------------------------

    def callback(self, event, x, y, flags, param):

        x = round(x / self.zoom) + self.x_offset
        y = round(y / self.zoom) + self.y_offset

        if event == cv2.EVENT_LBUTTONDOWN:
            # print("x: ", x, "y: ", y)
            self.left_flag = True
            if self.draw_check_box.checkState():
                self.drawMask([x*self.mult, y*self.mult])
                self.draw_count = 0
            else:
                # print("seg")
                self.points.append([x*self.mult,y*self.mult])
                self.labels.append(1)
                self.segmentation()

        if event == cv2.EVENT_LBUTTONUP:
            self.left_flag = False
        
        if event == cv2.EVENT_RBUTTONDOWN:
            # print("x: ", x, "y: ", y)
            self.right_flag = True
            if self.draw_check_box.checkState():
                self.drawMask([x*self.mult, y*self.mult])
                self.draw_count = 0
            else:
                # print("seg")
                self.points.append([x*self.mult,y*self.mult])
                self.labels.append(0)
                self.segmentation()

        if event == cv2.EVENT_RBUTTONUP:
            self.right_flag = False

        if (self.left_flag or self.right_flag) and (event == cv2.EVENT_MOUSEMOVE):
            if self.draw_count >= 5:
                self.drawMask([x*self.mult, y*self.mult])
                self.draw_count = 0
            self.draw_count += 1

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

    def segmentation(self):
        masks = self.model.forward(self.source_image, [self.points], [self.labels])

        mask = masks[2]  # [batch, point, num_masks, H, W] → [H, W]

        # self.current_object["mask_uint8"] = mask.astype(np.uint8)
        mask8 = mask.astype(np.uint8)

        self.current_object["mask"] = np.zeros((*mask8.shape, 3), dtype=np.uint8)  # shape: (H, W, 3)

        # Установим цвет для пикселей, где mask == 1
        self.current_object["mask"][mask8 == 1] = self.color  # BGR

        self.printMasks()

# -------------------------------------------------------------------------
# Рисование  
# -------------------------------------------------------------------------

    def drawMask(self, point):
        if len(self.current_object.keys()) == 0:
            self.current_object["mask"] = np.zeros_like(self.source_image)

        if self.left_flag:
            self.current_object["mask"] = cv2.circle(self.current_object["mask"], point, self.draw_size, self.color, self.draw_size*2)

        if self.right_flag:
            self.current_object["mask"] = cv2.circle(self.current_object["mask"], point, self.draw_size, (0,0,0), self.draw_size*2)
        
        self.printMasks()

# -------------------------------------------------------------------------
# Отрисовка маски 
# -------------------------------------------------------------------------

    def printMasks(self):
        self.masked_image = self.resized_image.copy()

        if len(self.current_object.keys()) > 0:
            mask = cv2.resize(self.current_object["mask"], (self.image_width, self.image_height))
            self.masked_image = cv2.addWeighted(self.masked_image, 1.0, mask, 0.90, 0)

        for obj in self.objects.keys():
            mask = cv2.resize(self.objects[obj]["mask"], (self.image_width, self.image_height))
            self.masked_image = cv2.addWeighted(self.masked_image, 1.0, mask, 0.90, 0)

        if len(self.current_object.keys()) > 0:
            bbox = self.getBoundingBox()
            self.masked_image = cv2.rectangle(self.masked_image, (bbox[0], bbox[1]), (bbox[2],bbox[3]), self.color, 1)

        img = self.masked_image.copy()
        img = img[
            self.y_offset : self.y_offset + self.new_height,
            self.x_offset : self.x_offset + self.new_width,
        ]

        img = cv2.resize(img, (self.masked_image.shape[1], self.masked_image.shape[0]))

        cv2.imshow("Image", img)

# -------------------------------------------------------------------------
# Генерация бокса
# -------------------------------------------------------------------------
    
    def getBoundingBox(self):
        
        # if not (self.mask_uint8 == None):
        # Находим координаты ненулевых пикселей (где mask == 1)

        mask8 = np.any(self.current_object["mask"] != 0, axis=-1).astype(np.uint8)

        ys, xs = np.where(mask8 > 0)

        # Проверка на случай, если маска пустая
        if len(xs) == 0 or len(ys) == 0:
            return (0,0,0,0)
        else:
            x_min, x_max = xs.min(), xs.max()
            y_min, y_max = ys.min(), ys.max()

            # Bounding box: (x_min, y_min) — левый верхний угол, (x_max, y_max) — правый нижний
            bbox = (x_min//self.mult, y_min//self.mult, x_max//self.mult, y_max//self.mult)
            return bbox

# -------------------------------------------------------------------------
# Завершение сегентации объекта 
# -------------------------------------------------------------------------

    def completeObject(self):
        if self.current_object_name not in self.objects.keys():
            self.objects_count[self.current_class] += 1

        if len(self.current_object.keys()) > 0:
            self.objects[self.current_object_name] = {}
            self.objects[self.current_object_name]["mask"] = self.current_object["mask"]

            self.points = []
            self.labels = []
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
        self.points = []
        self.labels = []
        print("Cancel")

        self.combobox_classes.setEnabled(True)
        self.delete_button.setEnabled(False)

        self.printMasks()

# -------------------------------------------------------------------------
# выбор объекта 
# -------------------------------------------------------------------------

    def selectObject(self):

        if not (self.objects_list.currentItem() is None):

            self.current_object_name = self.objects_list.currentItem().text()
            self.current_object = self.objects[self.current_object_name]
            self.current_class = self.current_object_name[0:self.current_object_name.find("_")]

            self.points = []
            self.labels = []
            self.color = self.classes_color[self.current_class]
            print("Select object: ", self.current_object_name)
            self.combobox_classes.setEnabled(False)
            self.delete_button.setEnabled(True)

            self.printMasks()

# -------------------------------------------------------------------------
# Удаление объекта
# -------------------------------------------------------------------------

    def deleteObject(self):

        if self.current_object_name in self.objects.keys():

            self.objects.pop(self.current_object_name)

            self.points = []
            self.labels = []
            self.current_object = {}

            print("Delete ", self.current_object_name)

            items = [self.objects_list.item(x).text() for x in range(self.objects_list.count())]
            if self.current_object_name in items:
                self.objects_list.takeItem(items.index(self.current_object_name))

            self.combobox_classes.setEnabled(True)
            self.delete_button.setEnabled(False)

            self.printMasks()

# -------------------------------------------------------------------------
# Формирование контура
# -------------------------------------------------------------------------

    def create_yolo_line_from_mask(self, class_id, mask, image_width, image_height):
        # Убедимся, что маска uint8
        binary_mask = (mask > 0).astype(np.uint8) * 255

        # Найдём внешние контуры (только один объект)
        contours, _ = cv2.findContours(binary_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if not contours:
            return None  # Ничего не нашли

        # Выберем самый большой по площади контур
        contour = max(contours, key=cv2.contourArea)
        
        # Вычислим bbox
        x, y, w, h = cv2.boundingRect(contour)
        x_center = (x + w / 2) / image_width
        y_center = (y + h / 2) / image_height
        width = w / image_width
        height = h / image_height

        # Преобразуем контур в YOLO-формат
        norm_points = []
        for pt in contour:
            px, py = pt[0]
            norm_x = px / image_width
            norm_y = py / image_height
            norm_points.append((norm_x, norm_y))

        # Соберём строку
        # bbox_part = f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}"
        mask_part = " ".join(f"{x:.6f} {y:.6f}" for (x, y) in norm_points)

        return f"{class_id} {mask_part}"
    
# -------------------------------------------------------------------------
# Генерация лейбла
# -------------------------------------------------------------------------

    def generateLable(self):
        with open("output/" + self.file_name[0:-4] + ".txt", "w") as f:
            for key in self.objects.keys():
                for i in range(len(self.classes)):
                    if self.classes[i] in key:
                        mask8 = np.any(self.objects[key]['mask'] != 0, axis=-1).astype(np.uint8)
                        line = self.create_yolo_line_from_mask(i, mask8, self.source_width, self.source_height)
                        f.write(line + "\n")
        # with open('../test.npy', 'wb') as f:
        #     np.save(f, self.mask_uint8)
        print(self.file_name[0:-4] + " Coplete!")

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

            self.points = []
            self.labels = []

            self.objects_list.clear()

            lines = f.readlines()

            h, w = self.source_image.shape[:2]

            # Перебираем все аннотированные объекты
            for line in lines:
                parts = line.strip().split()
                cls_id = int(parts[0])
                coords = list(map(float, parts[1:]))
                points = np.array([
                    [int(float(coords[i]) * w), int(float(coords[i+1]) * h)]
                    for i in range(0, len(coords), 2)
                ])
                
                name = self.classes[cls_id]+"_"+str(self.objects_count[self.classes[cls_id]])
                self.objects[name] = {}
                self.objects[name]["mask"] = np.zeros(self.source_image.shape, dtype=np.uint8)  # shape: (H, W, 3)
                self.objects_count[self.classes[cls_id]] += 1

                # Рисуем полигон
                cv2.polylines(self.objects[name]["mask"], [points], isClosed=True, color=self.classes_color[self.classes[cls_id]], thickness=2)
                cv2.fillPoly(self.objects[name]["mask"], [points], color=self.classes_color[self.classes[cls_id]])  # заливаем полигон полупрозрачным

                self.objects_list.addItem(name)

            self.current_object_name = self.current_class + "_" + str(self.objects_count[self.current_class])
            self.printMasks()
