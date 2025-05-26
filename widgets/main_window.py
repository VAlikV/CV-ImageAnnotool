
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
from widgets.sam import SAM
from widgets.sam2 import SAM2
import os
import cv2
import numpy as np

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.classes = ["Connector", "Conts"]
        self.current_class = self.classes[0]
        self.current_file_index = -1
        self.file_list = []

        # self.colors = ((255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255))
        self.color = [0,0,255]
        # np.random.uniform(0, 256, 3)

        self.segmented_objects = {}
        self.objects_count = {}
        self.masks = []

        for c in self.classes:
            self.objects_count[c] = 0

        self.zoom = 1
        self.min_zoom = 1
        self.max_zoom = 10
        self.x_offset, self.y_offset = 0, 0

        self.image_height, self.image_width = 480, 640
        self.new_height, self.new_width = self.image_height, self.image_width

        self.model = SAM2()
        self.points = []
        self.labels = []

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

        self.combobox_classes = QComboBox()
        self.combobox_classes.addItems(self.classes)
        self.middle_layout = QHBoxLayout()
        self.middle_layout.addWidget(QLabel("Class: "))
        self.middle_layout.addWidget(self.combobox_classes)

        # =======================================================

        self.cancel_button = QPushButton("Cancel")
        self.ok_button = QPushButton("Ok")
        self.generate_button = QPushButton("Generate")
        self.down_layout = QHBoxLayout()
        self.down_layout.addWidget(self.cancel_button)
        self.down_layout.addWidget(self.ok_button)
        self.down_layout.addWidget(self.generate_button)

        # =======================================================

        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.up_layout)
        self.main_layout.addLayout(self.middle_layout)
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
        # self.ok_button.clicked.connect(self.openFile)
        # self.combobox_classes.changeEvent(self.selectNewClass)
        self.combobox_classes.currentIndexChanged.connect(self.selectNewClass)
        self.ok_button.clicked.connect(self.completeObject)
        self.generate_button.clicked.connect(self.generateLable)

# -------------------------------------------------------------------------
# Обновление списка файлов 
# -------------------------------------------------------------------------

    def updateFileList(self):
        self.file_list = os.listdir("../input")

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
            self.segmented_objects = {}
            self.objects_count = {}
            self.masks = []

            for c in self.classes:
                self.objects_count[c] = 0

            self.image = cv2.imread("../input/" + self.file_name)
            self.image = cv2.resize(self.image, (self.image_width, self.image_height))
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
            self.points.append([x,y])
            self.labels.append(1)
            self.segmentation()
        
        if event == cv2.EVENT_RBUTTONDOWN:
            # print("x: ", x, "y: ", y)
            self.points.append([x,y])
            self.labels.append(0)
            self.segmentation()

        if event == cv2.EVENT_MOUSEWHEEL:
            if flags > 0:
                self.zoom *= 1.1
                self.zoom = min(self.zoom, self.max_zoom)
            else:
                self.zoom /= 1.1
                self.zoom = max(self.zoom, self.min_zoom)

            img = self.image.copy()

            # Calculate zoomed-in image size
            self.new_width = round(img.shape[1] / self.zoom)
            self.new_height = round(img.shape[0] / self.zoom)

            # Calculate offset
            self.x_offset = round(x - (x / self.zoom))
            self.y_offset = round(y - (y / self.zoom))

            # Crop image
            img = img[
                self.y_offset : self.y_offset + self.new_height,
                self.x_offset : self.x_offset + self.new_width,
            ]

            if cv2.getWindowProperty('Mask', cv2.WND_PROP_VISIBLE) >= 1:
                img2 = self.overlay.copy()
                img2 = img2[
                    self.y_offset : self.y_offset + self.new_height,
                    self.x_offset : self.x_offset + self.new_width,
                ]
                img2 = cv2.resize(img2, (self.image.shape[1], self.image.shape[0]))
                cv2.imshow("Mask", img2)

            # Stretch image to full size
            img = cv2.resize(img, (self.image.shape[1], self.image.shape[0]))
            cv2.imshow("Image", img)

# -------------------------------------------------------------------------
# Прямой проход по sam  
# -------------------------------------------------------------------------

    def segmentation(self):
        masks = self.model.forward(self.image, [self.points], [self.labels])

        mask = masks[2]  # [batch, point, num_masks, H, W] → [H, W]

        self.mask_uint8 = mask.astype(np.uint8)

        self.current_mask = np.zeros((*self.mask_uint8.shape, 3), dtype=np.uint8)  # shape: (H, W, 3)

        # Установим цвет для пикселей, где mask == 1
        self.current_mask[self.mask_uint8 == 1] = self.color  # BGR

        self.printMasks()

# -------------------------------------------------------------------------
# Отрисовка маски 
# -------------------------------------------------------------------------

    def printMasks(self):
        image_c = np.array(self.image)

        self.overlay = cv2.addWeighted(image_c, 1.0, self.current_mask, 0.75, 0)

        for m in self.masks:
            self.overlay = cv2.addWeighted(self.overlay, 1.0, m, 0.75, 0)

        bbox = self.getBoundingBox()
        self.overlay = cv2.rectangle(self.overlay, (bbox[0], bbox[1]), (bbox[2],bbox[3]), self.color, 1)

        img2 = self.overlay.copy()
        img2 = img2[
            self.y_offset : self.y_offset + self.new_height,
            self.x_offset : self.x_offset + self.new_width,
        ]

        img2 = cv2.resize(img2, (self.image.shape[1], self.image.shape[0]))

        cv2.imshow("Mask", img2)

# -------------------------------------------------------------------------
# Генерация бокса
# -------------------------------------------------------------------------
    
    def getBoundingBox(self):
        
        # Находим координаты ненулевых пикселей (где mask == 1)
        ys, xs = np.where(self.mask_uint8 > 0)

        # Проверка на случай, если маска пустая
        if len(xs) == 0 or len(ys) == 0:
            return (0,0,0,0)
        else:
            x_min, x_max = xs.min(), xs.max()
            y_min, y_max = ys.min(), ys.max()

            # Bounding box: (x_min, y_min) — левый верхний угол, (x_max, y_max) — правый нижний
            bbox = (x_min, y_min, x_max, y_max)
            return bbox

# -------------------------------------------------------------------------
# Выбор нового класса  
# -------------------------------------------------------------------------

    def selectNewClass(self):
        if not (self.combobox_classes.currentText() == self.current_class):
            # self.completeObject()
            self.current_class = self.combobox_classes.currentText()
            self.color = np.random.uniform(0, 256, 3)

# -------------------------------------------------------------------------
# Завершение сегентации объекта 
# -------------------------------------------------------------------------

    def completeObject(self):
        self.segmented_objects[self.current_class+"_"+str(self.objects_count[self.current_class])] = self.mask_uint8
        self.objects_count[self.current_class] += 1
        self.points = []
        self.labels = []
        self.masks.append(self.current_mask)
        print(self.segmented_objects.keys())

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
        with open("../output/" + self.file_name[0:-4] + ".txt", "w") as f:
            for key, value in self.segmented_objects.items():
                for i in range(len(self.classes)):
                    if self.classes[i] in key:
                        line = self.create_yolo_line_from_mask(i, value, self.image_width, self.image_height)
                        f.write(line + "\n")
        with open('../test.npy', 'wb') as f:
            np.save(f, self.mask_uint8)
        print(self.file_name[0:-4] + " Coplite!")
